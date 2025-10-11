"""
Seed sample payment transactions for testing
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import uuid
import os

# Connection to MongoDB
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'indowater_db')]


async def seed_payment_transactions():
    """Seed sample payment transactions"""
    
    # First, get the customer user ID
    customer = await db.users.find_one({"email": "customer@indowater.com"})
    
    if not customer:
        print("❌ Customer user not found. Please run seed_demo_users.py first")
        return
    
    customer_id = customer['id']
    
    # Sample transactions with different statuses
    transactions = [
        {
            "reference_id": f"IW-{datetime.now().strftime('%Y%m%d')}-001",
            "customer_id": customer_id,
            "customer_email": "customer@indowater.com",
            "customer_name": "John Customer",
            "customer_phone": "+62812345678",
            "meter_id": "METER-001",
            "amount": 100000,
            "payment_method": "midtrans",
            "status": "paid",
            "external_id": f"MT-{uuid.uuid4().hex[:10]}",
            "payment_url": None,
            "paid_at": (datetime.utcnow() - timedelta(days=2)).isoformat(),
            "created_at": (datetime.utcnow() - timedelta(days=2)).isoformat(),
            "updated_at": (datetime.utcnow() - timedelta(days=2)).isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
            "description": "Water balance top-up - 10 m³",
            "metadata": {"created_by": customer_id}
        },
        {
            "reference_id": f"IW-{datetime.now().strftime('%Y%m%d')}-002",
            "customer_id": customer_id,
            "customer_email": "customer@indowater.com",
            "customer_name": "John Customer",
            "customer_phone": "+62812345678",
            "meter_id": "METER-001",
            "amount": 250000,
            "payment_method": "xendit_va",
            "status": "paid",
            "external_id": f"XD-{uuid.uuid4().hex[:10]}",
            "payment_url": None,
            "va_number": "8808012345678901",
            "va_bank": "BCA",
            "paid_at": (datetime.utcnow() - timedelta(days=5)).isoformat(),
            "created_at": (datetime.utcnow() - timedelta(days=5)).isoformat(),
            "updated_at": (datetime.utcnow() - timedelta(days=5)).isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
            "description": "Water balance top-up - 25 m³",
            "metadata": {"created_by": customer_id}
        },
        {
            "reference_id": f"IW-{datetime.now().strftime('%Y%m%d')}-003",
            "customer_id": customer_id,
            "customer_email": "customer@indowater.com",
            "customer_name": "John Customer",
            "customer_phone": "+62812345678",
            "meter_id": "METER-001",
            "amount": 50000,
            "payment_method": "xendit_qris",
            "status": "paid",
            "external_id": f"XD-{uuid.uuid4().hex[:10]}",
            "payment_url": None,
            "qr_string": "00020101021126660014ID.CO.QRIS...",
            "paid_at": (datetime.utcnow() - timedelta(days=10)).isoformat(),
            "created_at": (datetime.utcnow() - timedelta(days=10)).isoformat(),
            "updated_at": (datetime.utcnow() - timedelta(days=10)).isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            "description": "Water balance top-up - 5 m³",
            "metadata": {"created_by": customer_id}
        },
        {
            "reference_id": f"IW-{datetime.now().strftime('%Y%m%d')}-004",
            "customer_id": customer_id,
            "customer_email": "customer@indowater.com",
            "customer_name": "John Customer",
            "customer_phone": "+62812345678",
            "meter_id": "METER-001",
            "amount": 500000,
            "payment_method": "xendit_ewallet",
            "status": "paid",
            "external_id": f"XD-{uuid.uuid4().hex[:10]}",
            "payment_url": None,
            "ewallet_type": "OVO",
            "paid_at": (datetime.utcnow() - timedelta(days=15)).isoformat(),
            "created_at": (datetime.utcnow() - timedelta(days=15)).isoformat(),
            "updated_at": (datetime.utcnow() - timedelta(days=15)).isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(minutes=30)).isoformat(),
            "description": "Water balance top-up - 50 m³",
            "metadata": {"created_by": customer_id, "ewallet_type": "OVO"}
        },
        {
            "reference_id": f"IW-{datetime.now().strftime('%Y%m%d')}-005",
            "customer_id": customer_id,
            "customer_email": "customer@indowater.com",
            "customer_name": "John Customer",
            "customer_phone": "+62812345678",
            "meter_id": "METER-001",
            "amount": 100000,
            "payment_method": "midtrans",
            "status": "pending",
            "external_id": f"MT-{uuid.uuid4().hex[:10]}",
            "payment_url": "https://app.sandbox.midtrans.com/snap/v2/...",
            "created_at": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "updated_at": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=22)).isoformat(),
            "description": "Water balance top-up - 10 m³",
            "metadata": {"created_by": customer_id, "snap_token": "sample-token-123"}
        },
        {
            "reference_id": f"IW-{datetime.now().strftime('%Y%m%d')}-006",
            "customer_id": customer_id,
            "customer_email": "customer@indowater.com",
            "customer_name": "John Customer",
            "customer_phone": "+62812345678",
            "meter_id": "METER-001",
            "amount": 150000,
            "payment_method": "xendit_va",
            "status": "expired",
            "external_id": f"XD-{uuid.uuid4().hex[:10]}",
            "payment_url": None,
            "va_number": "8808012345678902",
            "va_bank": "BNI",
            "created_at": (datetime.utcnow() - timedelta(days=3)).isoformat(),
            "updated_at": (datetime.utcnow() - timedelta(days=1)).isoformat(),
            "expires_at": (datetime.utcnow() - timedelta(days=1)).isoformat(),
            "description": "Water balance top-up - 15 m³",
            "metadata": {"created_by": customer_id}
        },
        {
            "reference_id": f"IW-{datetime.now().strftime('%Y%m%d')}-007",
            "customer_id": customer_id,
            "customer_email": "customer@indowater.com",
            "customer_name": "John Customer",
            "customer_phone": "+62812345678",
            "meter_id": "METER-001",
            "amount": 75000,
            "payment_method": "midtrans",
            "status": "failed",
            "external_id": f"MT-{uuid.uuid4().hex[:10]}",
            "payment_url": None,
            "created_at": (datetime.utcnow() - timedelta(days=7)).isoformat(),
            "updated_at": (datetime.utcnow() - timedelta(days=7)).isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
            "description": "Water balance top-up - 7.5 m³",
            "metadata": {"created_by": customer_id, "failure_reason": "Insufficient funds"}
        }
    ]
    
    # Clear existing test transactions
    result = await db.payment_transactions.delete_many({"customer_id": customer_id})
    print(f"🗑️  Deleted {result.deleted_count} existing transactions")
    
    # Insert new transactions
    result = await db.payment_transactions.insert_many(transactions)
    print(f"✅ Inserted {len(result.inserted_ids)} sample payment transactions")
    
    # Show summary
    print("\n📊 Transaction Summary:")
    print(f"   - Paid: {len([t for t in transactions if t['status'] == 'paid'])}")
    print(f"   - Pending: {len([t for t in transactions if t['status'] == 'pending'])}")
    print(f"   - Failed: {len([t for t in transactions if t['status'] == 'failed'])}")
    print(f"   - Expired: {len([t for t in transactions if t['status'] == 'expired'])}")
    print(f"\n💰 Total revenue (paid): Rp {sum(t['amount'] for t in transactions if t['status'] == 'paid'):,}")


if __name__ == '__main__':
    print("🌱 Seeding payment transactions...")
    asyncio.run(seed_payment_transactions())
    print("\n✅ Done!")
