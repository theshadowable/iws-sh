"""
Seed Water Conservation Tips for IndoWater
Run this script to populate water conservation tips in the database
"""
import os
import sys
from datetime import datetime
import uuid
from pymongo import MongoClient
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_mongo_url():
    """Get MongoDB URL with proper URL encoding"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    
    if '@' not in mongo_url:
        return mongo_url
    
    try:
        if mongo_url.startswith('mongodb+srv://'):
            protocol = 'mongodb+srv://'
        elif mongo_url.startswith('mongodb://'):
            protocol = 'mongodb://'
        else:
            return mongo_url
        
        url_without_protocol = mongo_url.replace(protocol, '', 1)
        last_at_index = url_without_protocol.rfind('@')
        
        if last_at_index == -1:
            return mongo_url
        
        credentials_part = url_without_protocol[:last_at_index]
        host_part = url_without_protocol[last_at_index + 1:]
        
        if ':' not in credentials_part:
            return mongo_url
        
        first_colon_index = credentials_part.find(':')
        username = credentials_part[:first_colon_index]
        password = credentials_part[first_colon_index + 1:]
        
        encoded_username = quote_plus(username)
        encoded_password = quote_plus(password)
        
        encoded_url = f"{protocol}{encoded_username}:{encoded_password}@{host_part}"
        return encoded_url
        
    except Exception as e:
        print(f"Error encoding MongoDB URL: {e}")
        return mongo_url

# Connect to MongoDB
mongo_url = get_mongo_url()
client = MongoClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'indowater_db')]

# Water conservation tips data
conservation_tips = [
    # General Savings
    {
        "title": "Matikan Keran Saat Menyikat Gigi",
        "description": "Jangan biarkan air mengalir saat Anda menyikat gigi. Gunakan gelas untuk berkumur. Tips sederhana ini bisa menghemat hingga 12 liter air per hari untuk setiap orang.",
        "category": "general_savings",
        "potential_savings_percentage": 15,
        "potential_savings_amount": 30000,
        "difficulty_level": "easy",
        "implementation_time": "Langsung",
        "tags": ["kamar mandi", "kebiasaan sehari-hari", "mudah"]
    },
    {
        "title": "Gunakan Shower Daripada Bathtub",
        "description": "Mandi dengan shower menggunakan air 40-60 liter, sedangkan bathtub bisa menghabiskan 150-200 liter. Batasi waktu shower Anda maksimal 5-7 menit untuk penghematan optimal.",
        "category": "general_savings",
        "potential_savings_percentage": 25,
        "potential_savings_amount": 50000,
        "difficulty_level": "easy",
        "implementation_time": "Langsung",
        "tags": ["kamar mandi", "shower", "hemat air"]
    },
    {
        "title": "Cuci Mobil Dengan Ember, Bukan Selang",
        "description": "Mencuci mobil dengan selang bisa menghabiskan 300-400 liter air. Gunakan ember dan spons, Anda hanya butuh 40-50 liter. Hemat hingga 350 liter per cuci mobil!",
        "category": "general_savings",
        "potential_savings_percentage": 30,
        "potential_savings_amount": 60000,
        "difficulty_level": "easy",
        "implementation_time": "10 menit",
        "tags": ["outdoor", "kendaraan", "penghematan besar"]
    },
    {
        "title": "Jalankan Mesin Cuci Hanya Saat Penuh",
        "description": "Tunggu sampai Anda punya cucian yang cukup untuk mengisi mesin cuci. Mesin cuci menggunakan air yang sama terlepas dari beban cucian, jadi maksimalkan setiap siklus pencucian.",
        "category": "general_savings",
        "potential_savings_percentage": 20,
        "potential_savings_amount": 40000,
        "difficulty_level": "easy",
        "implementation_time": "Langsung",
        "tags": ["laundry", "efisiensi", "rumah tangga"]
    },
    {
        "title": "Kumpulkan Air Dingin Saat Menunggu Air Panas",
        "description": "Saat menunggu air panas mengalir dari pemanas, tampung air dingin dengan ember. Air ini bisa digunakan untuk menyiram tanaman atau keperluan lainnya.",
        "category": "general_savings",
        "potential_savings_percentage": 10,
        "potential_savings_amount": 20000,
        "difficulty_level": "easy",
        "implementation_time": "5 menit",
        "tags": ["daur ulang air", "kreatif", "hemat"]
    },
    
    # Leak Prevention
    {
        "title": "Periksa Kebocoran Keran Secara Rutin",
        "description": "Keran yang menetes 1 tetes per detik bisa membuang 15 liter air per hari atau 450 liter per bulan! Periksa semua keran di rumah setiap minggu dan perbaiki segera jika ada kebocoran.",
        "category": "leak_prevention",
        "potential_savings_percentage": 35,
        "potential_savings_amount": 70000,
        "difficulty_level": "easy",
        "implementation_time": "15 menit per minggu",
        "tags": ["maintenance", "kebocoran", "inspeksi rutin"]
    },
    {
        "title": "Tes Kebocoran Toilet",
        "description": "Masukkan pewarna makanan ke dalam tangki toilet. Tunggu 15 menit tanpa menyiram. Jika ada warna di mangkuk toilet, berarti ada kebocoran. Toilet bocor bisa membuang hingga 200 liter air per hari!",
        "category": "leak_prevention",
        "potential_savings_percentage": 40,
        "potential_savings_amount": 80000,
        "difficulty_level": "easy",
        "implementation_time": "20 menit",
        "tags": ["toilet", "kebocoran tersembunyi", "tes sederhana"]
    },
    {
        "title": "Ganti Seal Keran Yang Aus",
        "description": "Seal karet pada keran bisa aus seiring waktu menyebabkan kebocoran. Ganti seal yang aus setiap 1-2 tahun untuk mencegah pemborosan air. Biaya seal sangat murah dibanding tagihan air yang terbuang.",
        "category": "leak_prevention",
        "potential_savings_percentage": 25,
        "potential_savings_amount": 50000,
        "difficulty_level": "medium",
        "implementation_time": "30 menit",
        "tags": ["perbaikan", "DIY", "maintenance"]
    },
    {
        "title": "Periksa Meteran Air Untuk Deteksi Kebocoran",
        "description": "Matikan semua keran dan peralatan yang menggunakan air. Catat angka meteran air. Tunggu 2 jam tanpa menggunakan air sama sekali. Jika angka meteran berubah, berarti ada kebocoran tersembunyi di sistem pipa Anda.",
        "category": "leak_prevention",
        "potential_savings_percentage": 30,
        "potential_savings_amount": 60000,
        "difficulty_level": "easy",
        "implementation_time": "2 jam",
        "tags": ["deteksi dini", "meter check", "kebocoran tersembunyi"]
    },
    {
        "title": "Insulasi Pipa Air di Musim Hujan",
        "description": "Pipa yang tidak terisolasi bisa retak karena tekanan air dan perubahan suhu. Lindungi pipa outdoor Anda dengan insulasi untuk mencegah kebocoran di masa depan.",
        "category": "leak_prevention",
        "potential_savings_percentage": 15,
        "potential_savings_amount": 30000,
        "difficulty_level": "medium",
        "implementation_time": "1-2 jam",
        "tags": ["preventif", "pipa", "cuaca"]
    },
    
    # Best Practices
    {
        "title": "Install Aerator pada Keran",
        "description": "Aerator mencampurkan udara dengan air, mengurangi aliran hingga 50% tanpa mengurangi tekanan. Harganya murah (Rp 20.000-50.000) dan bisa diinstall sendiri dalam 5 menit. Hemat 50 liter per hari untuk rumah tangga rata-rata!",
        "category": "best_practices",
        "potential_savings_percentage": 45,
        "potential_savings_amount": 90000,
        "difficulty_level": "easy",
        "implementation_time": "5 menit",
        "tags": ["upgrade", "aerator", "investasi kecil"]
    },
    {
        "title": "Gunakan Toilet Dual Flush",
        "description": "Toilet dual flush memiliki 2 tombol: flush kecil (3-4 liter) untuk cairan, flush besar (6 liter) untuk padat. Ini menghemat 30-50% dibanding toilet konvensional (9-12 liter per flush).",
        "category": "best_practices",
        "potential_savings_percentage": 35,
        "potential_savings_amount": 70000,
        "difficulty_level": "medium",
        "implementation_time": "1-2 jam (instalasi plumber)",
        "tags": ["toilet", "upgrade", "teknologi"]
    },
    {
        "title": "Pasang Rain Sensor di Taman",
        "description": "Jika Anda memiliki sistem irigasi otomatis, pasang rain sensor. Alat ini akan mematikan sistem saat hujan, mencegah penyiraman yang tidak perlu. Hemat hingga 100 liter per hari saat musim hujan!",
        "category": "best_practices",
        "potential_savings_percentage": 40,
        "potential_savings_amount": 80000,
        "difficulty_level": "medium",
        "implementation_time": "30 menit",
        "tags": ["taman", "otomasi", "smart home"]
    },
    {
        "title": "Gunakan Dishwasher Hemat Air",
        "description": "Dishwasher modern lebih hemat air daripada cuci piring manual (jika dijalankan saat penuh). Dishwasher hemat air hanya menggunakan 10-15 liter per siklus, vs 40-60 liter untuk cuci manual.",
        "category": "best_practices",
        "potential_savings_percentage": 30,
        "potential_savings_amount": 60000,
        "difficulty_level": "hard",
        "implementation_time": "2-3 jam (instalasi)",
        "tags": ["dapur", "teknologi", "efisien"]
    },
    {
        "title": "Mulching Tanaman Untuk Retensi Air",
        "description": "Taruh lapisan mulch (bahan organik seperti kulit kayu, kompos) setebal 5-10cm di sekitar tanaman. Mulch mengurangi evaporasi hingga 75%, menjaga kelembaban tanah lebih lama.",
        "category": "best_practices",
        "potential_savings_percentage": 25,
        "potential_savings_amount": 50000,
        "difficulty_level": "easy",
        "implementation_time": "1 jam",
        "tags": ["taman", "tanaman", "organik"]
    },
    
    # Saran Penghematan Air Prabayar
    {
        "title": "Monitor Penggunaan Air Real-Time via App",
        "description": "Dengan sistem prabayar IndoWater, Anda bisa memantau konsumsi air real-time. Cek app setiap hari untuk mengetahui pola penggunaan dan identifikasi pemborosan. Set target harian untuk kontrol lebih baik!",
        "category": "saran_penghematan_prabayar",
        "potential_savings_percentage": 20,
        "potential_savings_amount": 40000,
        "difficulty_level": "easy",
        "implementation_time": "5 menit per hari",
        "tags": ["prabayar", "monitoring", "app"]
    },
    {
        "title": "Set Alert Untuk Konsumsi Berlebih",
        "description": "Aktifkan notifikasi alert di app IndoWater. Anda akan mendapat peringatan jika konsumsi air melebihi rata-rata harian. Ini membantu mendeteksi kebocoran atau pemborosan dengan cepat.",
        "category": "saran_penghematan_prabayar",
        "potential_savings_percentage": 35,
        "potential_savings_amount": 70000,
        "difficulty_level": "easy",
        "implementation_time": "2 menit",
        "tags": ["prabayar", "alert", "deteksi dini"]
    },
    {
        "title": "Top-Up Saat Ada Promo Voucher",
        "description": "IndoWater sering memberikan voucher diskon untuk top-up. Simpan alert promo dan manfaatkan voucher untuk hemat biaya. Kombinasikan dengan penggunaan efisien untuk penghematan maksimal!",
        "category": "saran_penghematan_prabayar",
        "potential_savings_percentage": 15,
        "potential_savings_amount": 30000,
        "difficulty_level": "easy",
        "implementation_time": "Saat top-up",
        "tags": ["prabayar", "promo", "diskon"]
    },
    {
        "title": "Analisis Report Bulanan Anda",
        "description": "Download report penggunaan bulanan dari app IndoWater. Bandingkan dengan bulan sebelumnya untuk lihat progress penghematan. Identifikasi hari-hari dengan konsumsi tinggi dan cari penyebabnya.",
        "category": "saran_penghematan_prabayar",
        "potential_savings_percentage": 25,
        "potential_savings_amount": 50000,
        "difficulty_level": "easy",
        "implementation_time": "10 menit per bulan",
        "tags": ["prabayar", "analisis", "report"]
    },
    {
        "title": "Manfaatkan Fitur Water Usage Prediction",
        "description": "App IndoWater menggunakan AI untuk memprediksi konsumsi air Anda 7 hari ke depan. Gunakan prediksi ini untuk planning top-up dan mengantisipasi kebutuhan air Anda. Hindari kehabisan saldo mendadak!",
        "category": "saran_penghematan_prabayar",
        "potential_savings_percentage": 10,
        "potential_savings_amount": 20000,
        "difficulty_level": "easy",
        "implementation_time": "Langsung",
        "tags": ["prabayar", "AI", "prediksi"]
    },
    {
        "title": "Set Budget Bulanan di App",
        "description": "Tetapkan budget maksimal per bulan untuk konsumsi air. App akan tracking progress Anda dan memberi notifikasi jika mendekati limit. Cara efektif untuk kontrol pengeluaran dan disiplin penggunaan air!",
        "category": "saran_penghematan_prabayar",
        "potential_savings_percentage": 30,
        "potential_savings_amount": 60000,
        "difficulty_level": "easy",
        "implementation_time": "3 menit",
        "tags": ["prabayar", "budget", "kontrol"]
    },
    {
        "title": "Ikuti Challenge Penghematan Air",
        "description": "IndoWater mengadakan challenge bulanan untuk customer. Kurangi konsumsi air Anda sebanyak X% dan dapatkan reward voucher! Cara fun untuk hemat air sambil dapat benefit.",
        "category": "saran_penghematan_prabayar",
        "potential_savings_percentage": 20,
        "potential_savings_amount": 40000,
        "difficulty_level": "easy",
        "implementation_time": "1 bulan",
        "tags": ["prabayar", "challenge", "reward"]
    },
    {
        "title": "Bagikan Tips Hemat Air di Community",
        "description": "Bergabung dengan IndoWater Community di app. Bagikan tips penghematan Anda dan belajar dari user lain. Semakin banyak berbagi, semakin banyak ide hemat air yang Anda dapatkan!",
        "category": "saran_penghematan_prabayar",
        "potential_savings_percentage": 15,
        "potential_savings_amount": 30000,
        "difficulty_level": "easy",
        "implementation_time": "10 menit per minggu",
        "tags": ["prabayar", "komunitas", "sharing"]
    }
]

def seed_conservation_tips():
    """Seed water conservation tips to database"""
    try:
        # Get admin user (created_by field)
        admin = db.users.find_one({"role": "admin"})
        if not admin:
            print("⚠️ Warning: No admin user found. Using default admin ID.")
            admin_id = "default-admin-id"
        else:
            admin_id = admin['id']
        
        # Clear existing tips (optional - comment out if you want to keep existing tips)
        # db.water_conservation_tips.delete_many({})
        # print("🗑️ Cleared existing tips")
        
        # Insert tips
        inserted_count = 0
        updated_count = 0
        
        for tip_data in conservation_tips:
            # Check if tip already exists (by title)
            existing_tip = db.water_conservation_tips.find_one({"title": tip_data['title']})
            
            if existing_tip:
                # Update existing tip
                db.water_conservation_tips.update_one(
                    {"id": existing_tip['id']},
                    {"$set": {
                        **tip_data,
                        "updated_at": datetime.utcnow()
                    }}
                )
                updated_count += 1
                print(f"✏️ Updated: {tip_data['title']}")
            else:
                # Insert new tip
                tip_document = {
                    "id": str(uuid.uuid4()),
                    **tip_data,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "created_by": admin_id,
                    "is_active": True,
                    "view_count": 0,
                    "like_count": 0,
                    "implementation_count": 0
                }
                db.water_conservation_tips.insert_one(tip_document)
                inserted_count += 1
                print(f"✅ Inserted: {tip_data['title']}")
        
        print(f"\n🎉 Seeding completed!")
        print(f"📝 Inserted: {inserted_count} new tips")
        print(f"✏️ Updated: {updated_count} existing tips")
        print(f"📊 Total tips in database: {db.water_conservation_tips.count_documents({})}")
        
        # Print summary by category
        print("\n📋 Tips by category:")
        for category in ["general_savings", "leak_prevention", "best_practices", "saran_penghematan_prabayar"]:
            count = db.water_conservation_tips.count_documents({"category": category, "is_active": True})
            print(f"  - {category}: {count} tips")
        
        return True
        
    except Exception as e:
        print(f"❌ Error seeding tips: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🌊 IndoWater - Seeding Water Conservation Tips")
    print("=" * 60)
    
    success = seed_conservation_tips()
    
    if success:
        print("\n✅ Seeding successful!")
        sys.exit(0)
    else:
        print("\n❌ Seeding failed!")
        sys.exit(1)
