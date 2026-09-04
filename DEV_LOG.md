# Development Log: The 2 AM Failure

**The Incident:** 
During load testing the Agent-to-Agent negotiation flow, I discovered a critical race condition. Two independent AI buyer instances negotiated a price and attempted to purchase the last remaining `NVIDIA RTX 4090` at the exact same millisecond. Because the read and write operations were decoupled, both agents saw `stock_count = 1`, and both successfully generated Razorpay checkout links. The database stock dropped to `-1`.

**The Root Cause:**
The FastMCP server was executing standard `SELECT` queries to check stock, leaving a microscopic window between the read and the `UPDATE` where another thread could intervene. 

**The Fix:**
I immediately migrated the checkout tool to use strict row-level database locking via PostgreSQL's `SELECT ... FOR UPDATE` (`with_for_update()` in SQLAlchemy). 
Now, when an agent initiates a checkout, it physically locks that specific product row. If a second agent tries to buy it simultaneously, it is forced to wait until the first transaction commits or rolls back. 

**The Result:**
The system is now completely impervious to concurrency overselling. I wrote a strict asynchronous test (`tests/test_concurrency.py`) that fires two agents at the exact same time to prove exactly one succeeds while the other gracefully receives an "Out of Stock" rejection.