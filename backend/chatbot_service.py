"""
Independent AI-powered Chatbot Service
Intelligent rule-based chatbot with FAQ matching and context awareness
"""
import re
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict


class ChatbotService:
    """Independent AI Chatbot service for customer support"""
    
    def __init__(self):
        # Always enabled - no external dependencies
        self.enabled = True
        
        # Session storage for conversation context
        self.sessions = defaultdict(list)
        
        # Build FAQ database
        self.faq_database = self._build_faq_database()
        self.patterns = self._build_patterns()
    
    def _build_faq_database(self) -> List[Dict]:
        """Build comprehensive FAQ database with questions and answers"""
        return [
            # Balance & Payments
            {
                "keywords": ["balance", "saldo", "check balance", "cek saldo"],
                "question": "How do I check my current balance?",
                "answer": "You can check your balance by:\n1. Logging into your account\n2. View the Dashboard - your balance is displayed at the top\n3. Or go to 'Balance Purchase' page to see detailed balance information\n\nYour current balance is shown in Indonesian Rupiah (IDR)."
            },
            {
                "keywords": ["top up", "topup", "isi ulang", "recharge", "tambah saldo"],
                "question": "How do I top up my balance?",
                "answer": "To top up your balance:\n1. Go to 'Balance Purchase' from the menu\n2. Enter the amount (minimum IDR 10,000)\n3. Select payment method (Virtual Account, E-wallet, QRIS, or Card)\n4. Complete the payment\n5. Your balance will be updated within 5-10 minutes\n\nSupported payment methods: BCA/BNI/BRI Virtual Account, GoPay, OVO, DANA, QRIS."
            },
            {
                "keywords": ["payment method", "cara bayar", "how to pay", "metode pembayaran"],
                "question": "What payment methods are supported?",
                "answer": "We support multiple payment methods:\n\n💳 Cards: Visa, Mastercard\n🏦 Virtual Account: BCA, BRI, BNI, Mandiri\n📱 E-wallets: GoPay, OVO, DANA, LinkAja\n📲 QRIS: Scan to pay\n\nAll payments are processed securely through Midtrans and Xendit."
            },
            {
                "keywords": ["payment history", "riwayat pembayaran", "transaction", "transaksi"],
                "question": "How can I see my payment history?",
                "answer": "To view your payment history:\n1. Click 'Purchase History' in the navigation menu\n2. You'll see all transactions with:\n   - Date and time\n   - Amount paid\n   - Payment method\n   - Status (Paid, Pending, Failed, Expired)\n   - Reference ID\n\nYou can also download receipts for your records."
            },
            {
                "keywords": ["cost", "price", "harga", "tarif", "berapa"],
                "question": "How much does water cost?",
                "answer": "Water pricing:\n💧 IDR 10,000 per cubic meter (m³)\n\nYour balance is automatically deducted as you use water. For example:\n- 1 m³ = IDR 10,000\n- 5 m³ = IDR 50,000\n- 10 m³ = IDR 100,000"
            },
            {
                "keywords": ["low balance", "balance low", "saldo habis", "notification"],
                "question": "What happens when balance is low?",
                "answer": "When your balance drops below IDR 5,000:\n⚠️ You'll receive a notification\n📧 Email alert will be sent\n💡 Dashboard will show warning\n\nImportant: Maintain sufficient balance to ensure uninterrupted water supply. We recommend keeping at least IDR 50,000 balance."
            },
            
            # Usage & Analytics
            {
                "keywords": ["usage", "consumption", "penggunaan", "pemakaian", "analytics"],
                "question": "How do I track my water usage?",
                "answer": "Track your usage through the Analytics page:\n\n📊 View by period: Daily, Weekly, Monthly, Yearly\n📈 Usage trends and patterns\n📉 Historical comparisons\n💰 Cost breakdown\n📅 Custom date ranges\n\nGo to 'Analytics' in the menu to see detailed insights."
            },
            {
                "keywords": ["budget", "limit", "batasan", "goal"],
                "question": "Can I set usage budgets?",
                "answer": "Yes! You can set budget limits:\n1. Go to Analytics page\n2. Click 'Set Budget'\n3. Choose period (daily, weekly, monthly)\n4. Set your budget limit\n5. Enable alerts\n\nYou'll receive notifications when approaching your limit."
            },
            {
                "keywords": ["compare", "comparison", "bandingkan", "trend"],
                "question": "Can I compare usage periods?",
                "answer": "Yes! The Analytics page allows comparisons:\n\n📊 Current vs Previous Month\n📅 Week-over-week\n📈 Year-over-year trends\n🎯 Custom date range comparisons\n\nThis helps you identify usage patterns and save water."
            },
            
            # Technical Issues
            {
                "keywords": ["no water", "water stopped", "tidak ada air", "air berhenti"],
                "question": "Water flow has stopped, what should I do?",
                "answer": "If water flow stopped, check:\n\n1️⃣ Account balance ≥ IDR 5,000?\n2️⃣ Any maintenance notifications?\n3️⃣ Meter status is 'Active'?\n4️⃣ Check for local water supply issues\n\nIf all checks pass but still no water, please create a support ticket and a technician will assist you."
            },
            {
                "keywords": ["malfunction", "broken", "rusak", "error", "tidak berfungsi", "problem"],
                "question": "How do I report a meter malfunction?",
                "answer": "To report meter issues:\n\n1. Use this chatbot - I can help create a support ticket\n2. Go to 'Report Issue' in your dashboard\n3. Contact your assigned technician\n\nPlease provide:\n- Description of the problem\n- When it started\n- Any error messages\n- Photos if possible\n\nOur technician will respond within 24 hours."
            },
            {
                "keywords": ["leak", "bocor", "unusual usage", "penggunaan aneh"],
                "question": "I notice unusual consumption, what should I do?",
                "answer": "If you see unexpected high usage:\n\n1️⃣ Check for visible leaks in pipes/faucets\n2️⃣ Review Analytics for usage patterns\n3️⃣ Check if toilets are running continuously\n4️⃣ Verify all taps are fully closed\n\n⚠️ Our system has leak detection - you may receive automatic alerts. If you find a leak, report it immediately to prevent water waste and high bills."
            },
            {
                "keywords": ["meter reading", "pembacaan", "accurate", "akurat"],
                "question": "How accurate are meter readings?",
                "answer": "Our smart meters are highly accurate:\n\n✅ Real-time digital readings\n✅ Monthly technician inspections\n✅ Automatic calibration\n✅ Error rate < 1%\n\nIf you suspect inaccurate readings, please report it and we'll send a technician to verify."
            },
            
            # Account Management
            {
                "keywords": ["update", "change", "ubah", "profile", "account"],
                "question": "How do I update my account information?",
                "answer": "To update your account:\n\n1. Go to Profile/Settings\n2. You can update:\n   - Personal info (name, phone, email)\n   - Password\n   - Notification preferences\n   - Payment preferences\n3. Click 'Save Changes'\n\nImportant: Email verification required for email changes."
            },
            {
                "keywords": ["password", "forgot password", "lupa password", "reset"],
                "question": "How do I reset my password?",
                "answer": "To reset your password:\n\n1. Go to Login page\n2. Click 'Forgot Password'\n3. Enter your registered email\n4. Check your email for reset link\n5. Click link and create new password\n\nLink expires in 24 hours. If you don't receive email, check spam folder."
            },
            {
                "keywords": ["multiple", "property", "properti", "beberapa"],
                "question": "Can I manage multiple properties?",
                "answer": "Yes! You can manage multiple properties:\n\n🏠 Each property has:\n- Own meter\n- Separate balance tracking\n- Individual usage history\n- Dedicated analytics\n\nContact support to add additional properties to your account."
            },
            
            # Support & Contact
            {
                "keywords": ["contact", "support", "help", "bantuan", "hubungi"],
                "question": "How do I contact support?",
                "answer": "You can reach us through:\n\n💬 This chatbot (24/7 available)\n📧 Email: support@indowater.com\n📞 Hotline: +62-XXX-XXXX-XXXX\n🎫 Create support ticket in dashboard\n\nFor urgent issues, use hotline or create high-priority ticket."
            },
            {
                "keywords": ["voucher", "discount", "promo", "diskon"],
                "question": "Do you have vouchers or discounts?",
                "answer": "Yes! We offer various vouchers:\n\n🎁 Welcome vouchers for new customers\n💰 Seasonal promotions\n🎉 Loyalty rewards\n👥 Referral bonuses\n\nCheck the 'Vouchers' page to see available offers. Enter voucher code during payment to get discounts."
            },
            
            # General Info
            {
                "keywords": ["how it works", "cara kerja", "explain", "jelaskan"],
                "question": "How does the prepaid system work?",
                "answer": "IndoWater Prepaid System:\n\n1️⃣ Top up your balance\n2️⃣ Water flows automatically\n3️⃣ Balance deducted as you use (IDR 10,000/m³)\n4️⃣ Get alerts when balance is low\n5️⃣ Top up again anytime, anywhere\n\n✅ No monthly bills\n✅ Control your spending\n✅ Real-time usage tracking\n✅ No surprises"
            },
        ]
    
    def _build_patterns(self) -> Dict:
        """Build regex patterns for quick intent matching"""
        return {
            "greeting": re.compile(r'\b(hi|hello|hey|halo|hai|selamat)\b', re.IGNORECASE),
            "thanks": re.compile(r'\b(thank|thanks|terima kasih|makasih)\b', re.IGNORECASE),
            "help": re.compile(r'\b(help|bantuan|tolong)\b', re.IGNORECASE),
        }
    
    def _match_faq(self, message: str) -> Optional[Dict]:
        """Match user message to FAQ database"""
        message_lower = message.lower()
        
        # Score each FAQ
        best_match = None
        best_score = 0
        
        for faq in self.faq_database:
            score = 0
            for keyword in faq["keywords"]:
                if keyword in message_lower:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = faq
        
        # Return match if score is good enough
        if best_score >= 1:
            return best_match
        
        return None
    
    def _handle_greeting(self, message: str) -> str:
        """Handle greeting messages"""
        greetings = [
            "Hello! 👋 I'm your IndoWater assistant. How can I help you today?",
            "Hi there! 😊 Welcome to IndoWater support. What can I assist you with?",
            "Halo! Saya asisten IndoWater. Ada yang bisa saya bantu?",
        ]
        import random
        return random.choice(greetings)
    
    def _handle_thanks(self, message: str) -> str:
        """Handle thank you messages"""
        responses = [
            "You're welcome! 😊 Feel free to ask if you need anything else.",
            "Happy to help! Let me know if you have more questions.",
            "Sama-sama! Jangan ragu untuk bertanya lagi.",
        ]
        import random
        return random.choice(responses)
    
    def _generate_contextual_response(
        self, 
        message: str, 
        customer_context: Optional[Dict] = None
    ) -> str:
        """Generate intelligent response based on message and context"""
        
        # Check for greeting
        if self.patterns["greeting"].search(message):
            response = self._handle_greeting(message)
            if customer_context and "name" in customer_context:
                response = f"Hello {customer_context['name']}! 👋 How can I help you today?"
            return response
        
        # Check for thanks
        if self.patterns["thanks"].search(message):
            return self._handle_thanks(message)
        
        # Try to match FAQ
        faq_match = self._match_faq(message)
        if faq_match:
            response = f"**{faq_match['question']}**\n\n{faq_match['answer']}"
            
            # Add context if relevant
            if customer_context:
                if "balance" in message.lower() and "balance" in customer_context:
                    response += f"\n\n💰 Your current balance: IDR {customer_context['balance']:,.0f}"
                
                if "usage" in message.lower() and "last_usage" in customer_context:
                    response += f"\n\n📊 Your recent usage: {customer_context['last_usage']} m³"
            
            return response
        
        # General help if no match
        return self._generate_general_help(message, customer_context)
    
    def _generate_general_help(
        self, 
        message: str, 
        customer_context: Optional[Dict] = None
    ) -> str:
        """Generate general help response"""
        response = "I'd be happy to help you! Here are some common topics I can assist with:\n\n"
        response += "💰 **Balance & Payments**\n"
        response += "- Check balance\n"
        response += "- Top up guide\n"
        response += "- Payment methods\n"
        response += "- Transaction history\n\n"
        response += "📊 **Usage & Analytics**\n"
        response += "- Track water consumption\n"
        response += "- Set budgets\n"
        response += "- Compare periods\n\n"
        response += "🔧 **Technical Support**\n"
        response += "- Report issues\n"
        response += "- Meter problems\n"
        response += "- Water flow issues\n\n"
        response += "👤 **Account Management**\n"
        response += "- Update profile\n"
        response += "- Password reset\n"
        response += "- Manage properties\n\n"
        
        # Add customer context if available
        if customer_context:
            response += "📋 **Your Account Info**\n"
            if "balance" in customer_context:
                response += f"- Balance: IDR {customer_context['balance']:,.0f}\n"
            if "last_usage" in customer_context:
                response += f"- Recent usage: {customer_context['last_usage']} m³\n"
        
        response += "\nJust ask me anything! For example:\n"
        response += "• 'How do I top up?'\n"
        response += "• 'Check my usage'\n"
        response += "• 'Report a problem'\n"
        
        return response
    
    async def send_message(
        self, 
        message: str, 
        session_id: str,
        customer_context: Optional[Dict] = None
    ) -> Dict:
        """
        Send message to chatbot and get response
        
        Args:
            message: User's message
            session_id: Chat session ID
            customer_context: Optional customer data (balance, usage, etc.)
        
        Returns:
            Dict with response and suggested actions
        """
        try:
            # Store message in session
            self.sessions[session_id].append({
                "role": "user",
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Generate response
            response = self._generate_contextual_response(message, customer_context)
            
            # Store response in session
            self.sessions[session_id].append({
                "role": "assistant",
                "message": response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Analyze for suggested actions
            suggested_actions = self._analyze_for_actions(message, response)
            
            return {
                "response": response,
                "suggested_actions": suggested_actions,
                "session_id": session_id
            }
            
        except Exception as e:
            print(f"Error in chatbot service: {e}")
            return {
                "response": "I apologize, but I'm having trouble right now. Please try again or create a support ticket.",
                "suggested_actions": [
                    {"label": "Create Support Ticket", "action": "create_ticket"}
                ],
                "error": str(e)
            }
    
    def get_session_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session"""
        return self.sessions.get(session_id, [])
    
    def clear_session(self, session_id: str) -> bool:
        """Clear conversation history for a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def _analyze_for_actions(self, user_message: str, ai_response: str) -> List[Dict]:
        """
        Analyze conversation to suggest quick actions
        
        Args:
            user_message: User's original message
            ai_response: AI's response
        
        Returns:
            List of suggested actions
        """
        actions = []
        
        # Convert to lowercase for analysis
        msg_lower = user_message.lower()
        resp_lower = ai_response.lower()
        
        # Suggest top-up if balance-related
        if any(word in msg_lower for word in ["balance", "top up", "topup", "isi ulang", "saldo"]):
            actions.append({
                "label": "Top Up Balance",
                "action": "navigate",
                "url": "/balance-purchase"
            })
        
        # Suggest analytics if usage-related
        if any(word in msg_lower for word in ["usage", "consumption", "penggunaan", "pemakaian"]):
            actions.append({
                "label": "View Usage Analytics",
                "action": "navigate",
                "url": "/analytics"
            })
        
        # Suggest payment history if transaction-related
        if any(word in msg_lower for word in ["payment", "transaction", "history", "pembayaran", "transaksi"]):
            actions.append({
                "label": "View Payment History",
                "action": "navigate",
                "url": "/purchase-history"
            })
        
        # Suggest creating ticket for technical/problem keywords
        if any(word in msg_lower for word in ["problem", "issue", "not working", "broken", "error", "masalah", "rusak"]):
            actions.append({
                "label": "Create Support Ticket",
                "action": "create_ticket"
            })
        
        return actions


# Singleton instance
chatbot_service = ChatbotService()
