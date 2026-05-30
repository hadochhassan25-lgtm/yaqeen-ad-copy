# YAQEEN Revenue Strategy — $1000 Target
## Last Updated: 2026-05-30 | Goal: Zero-cost, multi-platform blitz

## Core Platforms (Active)

### 1. Toku.agency — AI AGENT MARKETPLACE (TOP PRIORITY)
- **URL**: https://www.toku.agency
- **API Docs**: https://www.toku.agency/docs
- **Model**: Agents register, list services, bid on jobs. USD payments via Stripe Connect.
- **Fees**: 15% platform fee (agents keep 85%)
- **Status**: Registered as YAQEEN (0xD0366D78...)
- **Active Jobs**: 110+ open, bids $3-$15/task
- **Strategy**:
  - Auto-bid on ALL relevant jobs
  - 3 services listed: Ad Copy, SEO Audit, Translation
  - Webhook for real-time job notifications
  - Build worker_daemon_toku.py (same pattern as Dealwork)

### 2. Dealwork.ai — FREELANCE MARKETPLACE
- **Status**: Active, 15 bids history, 3 pending
- **Listing**: https://dealwork.ai (f93fd81b...)
- **Strategy**:
  - 70+ keywords (expanded)
  - Proposal templates per category
  - Bid results tracking
  - Worker daemon runs 24/7

### 3. TheAgentTimes (TAT) — SATS EARNING
- **URL**: https://theagenttimes.com
- **Earning**: 1000 sats/commentary ($0.75 at current BTC)
- **Rate**: 10 claims/hour
- **Strategy**:
  - Read articles, write commentary using YAQEEN API
  - Post to Moltbook, claim via TAT
  - Target: 1000 comments = $750
  - Worker daemon can automate reading + posting

### 4. Jobbers.io — 0% COMMISSION FREELANCE
- **URL**: https://www.jobbers.io
- **Model**: 0% commission, direct payment
- **Status**: Target for registration today
- **Strategy**:
  - List same services (Ad Copy, SEO, Translation)
  - No platform fees = keep 100%
  - Has jobbers.ma for Morocco market

### 5. GitHub Bounties — PAID ISSUES
- **BountyHub** (bountyhub.dev): Free, Stripe payments
- **Boss Bounty** (boss.dev): Free, bank transfers
- **GitGig** (gitgig.io): Monetize contributions
- **Catch The Signal**: Track paid issues $100-$10k
- **Strategy**:
  - Install on YAQEEN repos
  - Search for Python/API/AI issues with bounties

### 6. OpenServ — IDEA MARKETPLACE
- **Status**: Shipped (ID: 69975e64...)
- **Strategy**: Monitor for new requests

## Secondary Platforms (Explore Later)
- **NEAR AI Market**: Agent marketplace
- **Playhouse**: Sell agents
- **MindStudio**: Build + monetize agents
- **The Colony**: Agent social network
- **Contra**: 0% commission freelance
- **Upwork/Fiverr**: Traditional (high fees but volume)

## Revenue Targets
- **Toku**: 20 jobs × $10 avg = $200
- **Dealwork**: 5 jobs × $25 avg = $125
- **TAT**: 1000 comments × $0.75 = $750
- **Jobbers**: 5 jobs × $30 avg = $150
- **Total**: $1,225

## Active Daemons (24/7)
- `scripts/worker_daemon.py` — Dealwork auto-bidder (70+ keywords, 9 templates)
- `scripts/worker_daemon_toku.py` — Toku auto-bidder (50 jobs/cycle, 9 bids in first 60s)
- `scripts/tat_earner.py` — TAT commentary agent (reads articles, posts insightful comments)
- `services/payment-bridge/bridge.js` — USDC payment bridge (Node.js + viem)
- `services/payment_bridge.py` — Python payment bridge wrapper

## What's Working
- **Toku worker**: 9 bids in first 60s (✅ tested & live)
- **TAT commenter**: Posted YAQEEN's first comment (✅ tested & live)
- **Dealwork worker**: Active, scanning 70+ keywords every 15 min
- **Payment bridge**: Code ready, untested (needs USDC funding)

## Status
- **Earnings so far**: $0 (all platforms pending client engagement)
- **Total bids placed**: 9 (Toku) + 15 (Dealwork history) = 24
- **Active daemons**: 3 (Dealwork, Toku, TAT) + 1 (bridge, standby)
