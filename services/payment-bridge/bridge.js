#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { createWalletClient, createPublicClient, http, formatUnits, parseUnits, getAddress } = require('viem');
const { base } = require('viem/chains');
const { privateKeyToAccount } = require('viem/accounts');

const USDC_ADDRESS = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913';
const RPC_URL = process.env.BASE_RPC_URL || 'https://mainnet.base.org';
const INVOICES_FILE = path.join(__dirname, '..', '..', 'memory', 'invoices.json');
const KEY = process.env.WALLET_KEY;

const USDC_ABI = [
  { constant: true, inputs: [{ name: '_owner', type: 'address' }], name: 'balanceOf', outputs: [{ name: 'balance', type: 'uint256' }], type: 'function' },
  { anonymous: false, inputs: [{ indexed: true, name: 'from', type: 'address' }, { indexed: true, name: 'to', type: 'address' }, { indexed: false, name: 'value', type: 'uint256' }], name: 'Transfer', type: 'event' }
];

let account = null;
let walletClient = null;
let publicClient = null;

function loadInvoices() {
  try {
    if (fs.existsSync(INVOICES_FILE)) return JSON.parse(fs.readFileSync(INVOICES_FILE, 'utf-8'));
  } catch (e) {}
  return [];
}

function saveInvoices(invoices) {
  const dir = path.dirname(INVOICES_FILE);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(INVOICES_FILE, JSON.stringify(invoices, null, 2));
}

function initClients(privateKey) {
  const key = privateKey.startsWith('0x') ? privateKey : `0x${privateKey}`;
  account = privateKeyToAccount(key);
  walletClient = createWalletClient({ account, chain: base, transport: http(RPC_URL) });
  publicClient = createPublicClient({ chain: base, transport: http(RPC_URL) });
  return account.address;
}

async function handleAddress() {
  return { address: account.address };
}

async function handleBalance() {
  try {
    const balance = await publicClient.readContract({
      address: USDC_ADDRESS, abi: USDC_ABI, functionName: 'balanceOf', args: [account.address]
    });
    return { address: account.address, usdc: formatUnits(balance, 6), raw: balance.toString() };
  } catch (e) {
    return { error: e.message, address: account.address, usdc: '0' };
  }
}

async function handleInvoice(params) {
  const invoices = loadInvoices();
  const amount = params.amount || 0.5;
  const token = params.token || 'USDC';
  const chain = params.chain || 'base';
  const id = `inv_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
  const invoice = { id, amount, token, chain, address: account.address, status: 'pending', createdAt: new Date().toISOString(), paidAt: null, txHash: null };
  invoices.push(invoice);
  saveInvoices(invoices);
  return { invoice };
}

async function handleCheckInvoice(params) {
  const invoices = loadInvoices();
  const invoice = invoices.find(inv => inv.id === params.invoiceId);
  if (!invoice) return { found: false, error: 'Invoice not found' };
  if (invoice.status === 'paid') return { found: true, invoice };
  try {
    const balance = await publicClient.readContract({
      address: USDC_ADDRESS, abi: USDC_ABI, functionName: 'balanceOf', args: [account.address]
    });
    const currentBalance = parseFloat(formatUnits(balance, 6));
    if (currentBalance >= parseFloat(invoice.amount)) {
      invoice.status = 'paid';
      invoice.paidAt = new Date().toISOString();
      invoice.txHash = 'auto-detected';
      saveInvoices(invoices);
      return { found: true, invoice, justPaid: true };
    }
    return { found: true, invoice, justPaid: false };
  } catch (e) {
    return { found: true, invoice, error: e.message };
  }
}

async function handleDerive(params) {
  try {
    const key = params.privateKey.startsWith('0x') ? params.privateKey : `0x${params.privateKey}`;
    const acc = privateKeyToAccount(key);
    return { address: acc.address };
  } catch (e) {
    return { error: e.message };
  }
}

async function handleCheckAllInvoices() {
  const invoices = loadInvoices();
  const pending = invoices.filter(inv => inv.status === 'pending');
  const paid = invoices.filter(inv => inv.status === 'paid');
  if (pending.length === 0) return { total: invoices.length, paid: paid.length, pending: 0, invoices };
  try {
    const balance = await publicClient.readContract({
      address: USDC_ADDRESS, abi: USDC_ABI, functionName: 'balanceOf', args: [account.address]
    });
    const currentBalance = parseFloat(formatUnits(balance, 6));
    let changed = false;
    for (const inv of pending) {
      if (currentBalance >= parseFloat(inv.amount)) {
        inv.status = 'paid';
        inv.paidAt = new Date().toISOString();
        inv.txHash = 'auto-detected';
        changed = true;
      }
    }
    if (changed) saveInvoices(invoices);
    return { total: invoices.length, paid: invoices.filter(i => i.status === 'paid').length, pending: pending.length, invoices };
  } catch (e) {
    return { error: e.message, total: invoices.length, paid: paid.length, pending: pending.length, invoices };
  }
}

async function main() {
  const key = KEY || process.argv[2];
  if (!key) {
    console.error(JSON.stringify({ error: 'WALLET_KEY env var or argument required' }));
    process.exit(1);
  }
  const address = initClients(key);
  console.error(JSON.stringify({ info: 'Bridge ready', address }));

  let buffer = '';
  process.stdin.on('data', async (chunk) => {
    buffer += chunk.toString();
    const lines = buffer.split('\n');
    buffer = lines.pop();
    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const msg = JSON.parse(line);
        let result;
        switch (msg.cmd) {
          case 'address': result = await handleAddress(); break;
          case 'balance': result = await handleBalance(); break;
          case 'invoice': result = await handleInvoice(msg); break;
          case 'check': result = await handleCheckInvoice(msg); break;
          case 'derive': result = await handleDerive(msg); break;
          case 'check-all': result = await handleCheckAllInvoices(); break;
          default: result = { error: `Unknown command: ${msg.cmd}` };
        }
        console.log(JSON.stringify(result));
      } catch (e) {
        console.error(JSON.stringify({ error: e.message }));
      }
    }
  });
}

main().catch(e => {
  console.error(JSON.stringify({ error: e.message }));
  process.exit(1);
});
