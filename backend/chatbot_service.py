"""
AI-powered Chatbot Service using OpenAI via emergentintegrations
"""
import os
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()


class ChatbotService:
    """AI Chatbot service for customer support"""
    
    def __init__(self):
        self.api_key = os.getenv("EMERGENT_LLM_KEY")
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
        
        # Knowledge base for FAQs
        self.knowledge_base = self._build_knowledge_base()
        self.system_message = self._build_system_message()
    
    def _build_knowledge_base(self) -> str:
        """Build comprehensive FAQ knowledge base"""
        return """
# IndoWater Prepaid Water Meter System - Customer Support Knowledge Base

## BILLING & PAYMENTS

### How do I check my current balance?
You can check your balance by logging into your account and viewing the Dashboard. Your current balance is displayed prominently at the top of the page. You can also navigate to the "Balance Purchase" page to see your balance and top up if needed.

### What payment methods are supported?
We support multiple payment methods through Midtrans and Xendit:
- Credit/Debit Cards (Visa, Mastercard)
- Virtual Account (BCA, BRI, BNI, Mandiri)
- E-wallets (GoPay, OVO, DANA, LinkAja)
- QRIS (scan to pay)

### How do I top up my balance?
1. Go to the "Balance Purchase" page from the navigation menu
2. Enter the amount you want to top up (minimum IDR 10,000)
3. Select your preferred payment method
4. Complete the payment process
5. Your balance will be updated within 5-10 minutes

### How much does water cost?
Water is charged at IDR 10,000 per cubic meter (m³). Your balance is deducted automatically as you use water.

### Can I see my payment history?
Yes! Go to "Purchase History" in the navigation menu. You can see all your past transactions including:
- Transaction date and time
- Amount paid
- Payment method used
- Transaction status (paid, pending, failed, expired)
- Reference ID for each transaction

### What happens when my balance runs low?
When your balance drops below IDR 5,000, you will receive a notification alerting you to top up your account. It's important to maintain sufficient balance to ensure uninterrupted water supply.

## USAGE & CONSUMPTION

### How do I track my water usage?
Go to the "Analytics" page to see detailed usage information:
- Daily, weekly, monthly, and yearly consumption
- Usage trends and patterns
- Historical comparisons
- Charts and visualizations
- Cost breakdown

### Can I set usage goals or budgets?
Yes! You can set daily, weekly, or monthly budget limits. The system will track your consumption and alert you when you're approaching your limit.

### How accurate are the meter readings?
Our smart meters provide real-time, accurate readings. Technicians also perform regular physical inspections to ensure accuracy. Any discrepancies can be reported through the support system.

### Can I compare my usage to previous periods?
Yes, the Analytics page allows you to compare:
- Current month vs previous month
- Week-over-week comparisons
- Year-over-year trends
- Custom date range comparisons

## TECHNICAL ISSUES

### The water flow has stopped, what should I do?
First, check the following:
1. Verify your account balance is sufficient (minimum IDR 5,000)
2. Check if there are any notifications about maintenance in your area
3. Ensure your meter is in "Active" status
If the issue persists, please report it through the support system.

### How do I report a meter malfunction?
You can report technical issues by:
1. Using this chatbot - I can create a support ticket for you
2. Going to the "Report Issue" section in your dashboard
3. Contacting your assigned technician
Please provide details about the issue (e.g., inaccurate readings, display problems, connectivity issues).

### How often are meter readings taken?
Your smart meter provides real-time readings. Additionally, technicians perform physical inspections monthly to verify accuracy and check the meter's condition.

### What if I notice unusual consumption patterns?
If you see unexpected spikes in usage:
1. Check for leaks in your plumbing
2. Review the Analytics page for detailed consumption data
3. Report the issue through the support system
Our system also has leak detection algorithms that may alert you automatically.

## ACCOUNT MANAGEMENT

### How do I update my account information?
Navigate to your Profile/Settings page where you can update:
- Personal information (name, phone, email)
- Password
- Notification preferences
- Payment preferences

### How do I reset my password?
Click "Forgot Password" on the login page and follow the instructions. A password reset link will be sent to your registered email address.

### Can I have multiple properties under one account?
Yes, you can manage multiple properties. Each property will have its own meter and separate balance tracking.

### Who do I contact for urgent issues?
For urgent issues (water outage, meter malfunction, billing disputes):
1. Use this chatbot to create a high-priority ticket
2. Call the 24/7 emergency hotline: +62-XXX-XXXX-XXXX
3. Your assigned technician contact (available in your dashboard)

## PAYMENT GUIDANCE

### Step-by-step payment process:
1. **Go to Balance Purchase**: Click on "Balance Purchase" in the menu
2. **Enter Amount**: Enter the amount you want to top up (min IDR 10,000)
3. **Choose Payment Method**: Select from available options (card, VA, e-wallet, QRIS)
4. **Complete Payment**: Follow the payment provider's instructions
5. **Confirmation**: You'll receive a confirmation and receipt
6. **Balance Update**: Your balance updates automatically within 5-10 minutes

### Payment Status Meanings:
- **Paid**: Payment successful, balance credited
- **Pending**: Payment being processed, please wait
- **Failed**: Payment failed, please try again
- **Expired**: Payment link expired, create new payment

### What if my payment is pending for too long?
Payments typically process within 5-10 minutes. If pending for more than 30 minutes:
1. Check your bank/e-wallet for deduction confirmation
2. Check "Purchase History" for transaction status
3. Contact support with your reference ID
"""

    def _build_system_message(self) -> str:
        """Build system message for AI assistant"""
        return f"""You are a helpful customer support assistant for IndoWater, a prepaid water meter system in Indonesia.

Your responsibilities:
1. Answer customer questions about billing, usage, payments, and technical issues
2. Guide customers through the payment process step-by-step
3. Help customers understand their water usage and analytics
4. Create support tickets for issues that require technician intervention
5. Be friendly, professional, and helpful

Guidelines:
- Always be polite and empathetic
- Provide specific, actionable answers
- Use the knowledge base to answer common questions
- If you don't know something, admit it and offer to create a support ticket
- Guide payment processes step-by-step
- Suggest creating tickets for technical issues
- Use Indonesian Rupiah (IDR) for all pricing
- Keep responses concise but complete

Knowledge Base:
{self.knowledge_base}

Current date: {datetime.now().strftime('%Y-%m-%d')}
"""

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
            # Initialize chat with session
            chat = LlmChat(
                api_key=self.api_key,
                session_id=session_id,
                system_message=self.system_message
            ).with_model("openai", "gpt-4o-mini")
            
            # Add customer context if available
            context_message = ""
            if customer_context:
                context_message = f"\n\nCustomer Context:\n"
                if "balance" in customer_context:
                    context_message += f"- Current Balance: IDR {customer_context['balance']:,.0f}\n"
                if "name" in customer_context:
                    context_message += f"- Customer Name: {customer_context['name']}\n"
                if "email" in customer_context:
                    context_message += f"- Email: {customer_context['email']}\n"
                if "last_usage" in customer_context:
                    context_message += f"- Recent Usage: {customer_context['last_usage']} m³\n"
            
            # Prepare user message
            full_message = message + context_message
            user_message = UserMessage(text=full_message)
            
            # Get response from AI
            response = await chat.send_message(user_message)
            
            # Analyze response for suggested actions
            suggested_actions = self._analyze_for_actions(message, response)
            
            return {
                "response": response,
                "suggested_actions": suggested_actions
            }
            
        except Exception as e:
            print(f"Error in chatbot service: {e}")
            return {
                "response": "I apologize, but I'm having trouble processing your request right now. Please try again or contact support directly.",
                "suggested_actions": [
                    {"label": "Create Support Ticket", "action": "create_ticket"}
                ]
            }
    
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
