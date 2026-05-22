import { JsonRpcProvider, Wallet, Contract, Signature } from 'ethers'
import { EthersV6Adapter } from '@cowprotocol/sdk-ethers-v6-adapter'
import { setGlobalAdapter } from '@cowprotocol/sdk-common'
import {
  TradingSdk, OrderKind, OrderBookApi, SupportedChainId,
  OrderSigningUtils, generateAppDataFromDoc, buildAppData
} from '@cowprotocol/cow-sdk'

const PRIVATE_KEY = '0x76f99c0ecad9c0b52d30764326acdd5cf2540b9f3af36276d023890fe1a04550'
const WALLET = '0xD0366D78055b8c637c44d769D1A1371106d13552' as `0x${string}`
const USDC = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48' as `0x${string}`
const WETH = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2' as `0x${string}`
const VAULT_RELAYER = '0xC92E8bdf79f0507f65a392b0ab4667716BFE0110' as `0x${string}`
const SELL_AMOUNT = '2140000'
const RPC_URL = 'https://ethereum-rpc.publicnode.com'
const CHAIN_ID = SupportedChainId.MAINNET

const PERMIT_ABI = [
  'function DOMAIN_SEPARATOR() view returns (bytes32)',
  'function nonces(address) view returns (uint256)',
  'function balanceOf(address) view returns (uint256)',
  'function allowance(address,address) view returns (uint256)',
]

async function main() {
  const provider = new JsonRpcProvider(RPC_URL, 1, { staticNetwork: true })
  const wallet = new Wallet(PRIVATE_KEY, provider)

  const adapter = new EthersV6Adapter({ provider, signer: wallet })
  setGlobalAdapter(adapter)

  // --- Check USDC EIP-2612 support ---
  const usdc = new Contract(USDC, PERMIT_ABI, provider)
  const ds = await usdc.DOMAIN_SEPARATOR()
  const nonce = await usdc.nonces(WALLET)
  const bal = await usdc.balanceOf(WALLET)
  const allowance = await usdc.allowance(WALLET, VAULT_RELAYER)
  console.log('=== USDC Info ===')
  console.log('Balance:', bal.toString())
  console.log('DOMAIN_SEPARATOR:', ds)
  console.log('Nonce:', nonce.toString())
  console.log('Allowance for VaultRelayer:', allowance.toString())
  console.log('EIP-2612 supported: YES\n')

  // --- Get quote ---
  const sdk = new TradingSdk({ chainId: CHAIN_ID, appCode: 'MoltbookTest' })
  console.log('--- Getting quote ---')
  const quote = await sdk.getQuoteOnly({
    owner: WALLET,
    kind: OrderKind.SELL,
    sellToken: USDC,
    sellTokenDecimals: 6,
    buyToken: WETH,
    buyTokenDecimals: 18,
    amount: SELL_AMOUNT,
  })

  console.log('App data hash:', quote.appDataInfo.appDataKeccak256)
  console.log('App data doc:', JSON.stringify(quote.appDataInfo.doc, null, 2))
  console.log('Slippage (bps):', quote.suggestedSlippageBps)
  console.log('Quote verified:', quote.quoteResponse.verified)
  console.log('Quote ID:', quote.quoteResponse.id, '\n')

  // --- Build appData with EIP-2612 permit as pre-interaction ---
  // The permit function: permit(owner, spender, value, deadline, v, r, s)
  // 1. Create the permit message
  const PERMIT_TYPES = {
    Permit: [
      { name: 'owner', type: 'address' },
      { name: 'spender', type: 'address' },
      { name: 'value', type: 'uint256' },
      { name: 'nonces', type: 'uint256' },
      { name: 'deadline', type: 'uint256' },
    ],
  }

  const deadline = Math.floor(Date.now() / 1000) + 3600 // 1 hour

  const permitMessage = {
    owner: WALLET,
    spender: VAULT_RELAYER,
    value: '2140000',
    nonces: nonce,
    deadline,
  }

  const permitDomain = {
    name: 'USD Coin',
    version: '2',
    chainId: 1,
    verifyingContract: USDC,
  }

  const permitSignature = await wallet.signTypedData(permitDomain, PERMIT_TYPES, permitMessage)
  const sig = Signature.from(permitSignature)
  const v = sig.v
  const r = sig.r
  const s = sig.s

  // 2. Encode the permit call data
  const permitCallData = new Contract(USDC, [
    'function permit(address owner, address spender, uint256 value, uint256 deadline, uint8 v, bytes32 r, bytes32 s)',
  ]).interface.encodeFunctionData('permit', [WALLET, VAULT_RELAYER, '2140000', deadline, v, r, s])

  // 3. Build appData with the permit pre-hook
  const appDataDoc = {
    ...quote.appDataInfo.doc,
    metadata: {
      ...quote.appDataInfo.doc.metadata,
      hooks: {
        pre: [
          {
            target: USDC,
            callData: permitCallData,
            gasLimit: '100000',
          },
        ],
      },
    },
  }

  const appDataInfo = await generateAppDataFromDoc(appDataDoc)
  console.log('Custom appData hash (with permit pre-hook):', appDataInfo.appDataKeccak256)

  // 4. Upload appData to the API
  const orderBookApi = new OrderBookApi({ chainId: CHAIN_ID })
  await orderBookApi.uploadAppData(appDataInfo.appDataKeccak256, appDataInfo.fullAppData!)
  console.log('AppData uploaded successfully')

  // 5. Sign the order
  const orderToSign = {
    ...quote.orderToSign,
    appData: appDataInfo.appDataKeccak256,
  }

  const signer = adapter.signer
  const { signature: orderSignature, signingScheme } = await OrderSigningUtils.signOrder(
    orderToSign,
    CHAIN_ID,
    signer
  )
  console.log('Order signed, scheme:', signingScheme)

  // 6. Post the order
  console.log('\n--- Posting order with EIP-2612 permit pre-interaction ---')
  const orderBody = {
    ...orderToSign,
    from: WALLET,
    signature: orderSignature,
    signingScheme: signingScheme as any,
    quoteId: quote.quoteResponse.id ?? null,
    appData: appDataInfo.fullAppData!,
    appDataHash: appDataInfo.appDataKeccak256,
  }

  const orderId = await orderBookApi.sendOrder(orderBody)
  console.log('\n=== ORDER POSTED SUCCESSFULLY ===')
  console.log('Order ID:', orderId)
  console.log('Signing Scheme:', signingScheme)
  console.log('Signature:', orderSignature.slice(0, 66) + '...')
  console.log('App data hash:', appDataInfo.appDataKeccak256)
  console.log('Full appData:', appDataInfo.fullAppData)
}

main().catch((err: any) => {
  console.error('\n=== ERROR ===')
  if (err.body) {
    console.error('API errorType:', err.body.errorType)
    console.error('API description:', err.body.description)
  } else {
    console.error(err.message || err)
  }
  process.exit(1)
})
