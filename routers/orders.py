from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from database import get_db
from models import Order, OrderItem
from schemas import OrderCreate, OrderResponse, OrderUpdate
import httpx
import os

router = APIRouter()

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
OWNER_EMAIL = os.getenv("OWNER_EMAIL", "kane.soutoura.ks@gmail.com")

@router.get("/", response_model=List[OrderResponse])
def get_orders(db: Session = Depends(get_db)):
    """Get all orders with their items"""
    orders = db.query(Order).order_by(Order.created_at.desc()).all()
    return orders

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get a single order by ID with its items"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    return order

@router.post("/", status_code=201)
async def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order and send email notification"""
    
    # Create order
    db_order = Order(
        customer_name=order_data.customer_name,
        customer_email=order_data.customer_email,
        customer_phone=order_data.customer_phone,
        customer_address=order_data.customer_address,
        payment_method=order_data.payment_method,
        total_amount=order_data.total_amount,
        status="en cours"
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    for item in order_data.items:
        db_item = OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            product_name=item.product_name,
            quantity=item.quantity,
            price=item.price,
            size=item.size,
            color=item.color
        )
        db.add(db_item)
    
    db.commit()
    
    # Send email notification
    try:
        items_html = ""
        for item in order_data.items:
            total_item = item.price * item.quantity
            size_color_info = ""
            if item.size or item.color:
                details = []
                if item.size:
                    details.append(f"Taille: {item.size}")
                if item.color:
                    details.append(f"Couleur: {item.color}")
                size_color_info = f"<br><small style='color: #666;'>({', '.join(details)})</small>"
            
            items_html += f"""
                <tr>
                    <td><strong>{item.product_name}</strong>{size_color_info}</td>
                    <td style="text-align: center;">{item.quantity}</td>
                    <td style="text-align: right;">{item.price:,.0f} FCFA</td>
                    <td style="text-align: right;"><strong>{total_item:,.0f} FCFA</strong></td>
                </tr>
            """
        
        email_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #C08831 0%, #995A46 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .logo {{ width: 80px; height: 80px; margin: 0 auto 15px; }}
            .content {{ background: white; padding: 30px; border: 1px solid #e0e0e0; }}
            .order-number {{ font-size: 24px; font-weight: bold; color: #C08831; margin-bottom: 20px; }}
            .section {{ margin-bottom: 25px; }}
            .section-title {{ font-size: 18px; font-weight: bold; color: #301B18; margin-bottom: 10px; border-bottom: 2px solid #C08831; padding-bottom: 5px; }}
            .info-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f0f0f0; }}
            .info-label {{ font-weight: 600; color: #995A46; }}
            .info-value {{ color: #301B18; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th {{ background-color: #C08831; color: white; padding: 12px; text-align: left; }}
            td {{ padding: 12px; border-bottom: 1px solid #e0e0e0; }}
            tr:hover {{ background-color: #f9f9f9; }}
            .total-row {{ background-color: #FFF8E7; font-weight: bold; font-size: 18px; }}
            .total-row td {{ color: #C08831; padding: 15px 12px; }}
            .footer {{ background-color: #301B18; color: white; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; margin-top: 20px; }}
            .badge {{ display: inline-block; padding: 5px 15px; background-color: #4CAF50; color: white; border-radius: 20px; font-size: 12px; font-weight: bold; }}
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <img src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/soutoura_logo-NWZB10FOtFdaOiZUZdvV0TEZqtpf70.png" alt="SOUTOURA_KS Logo" class="logo">
              <h1 style="margin: 0; font-size: 28px;">SOUTOURA_KS</h1>
              <p style="margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;">Nouvelle commande reçue</p>
            </div>
            
            <div class="content">
              <div class="order-number">
                Commande #{db_order.id} <span class="badge">NOUVELLE</span>
              </div>
              
              <div class="section">
                <div class="section-title">📋 Informations Client</div>
                <div class="info-row">
                  <span class="info-label">Nom complet:</span>
                  <span class="info-value">{order_data.customer_name}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Email:</span>
                  <span class="info-value">{order_data.customer_email}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Téléphone:</span>
                  <span class="info-value">{order_data.customer_phone}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Adresse de livraison:</span>
                  <span class="info-value">{order_data.customer_address}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Mode de paiement:</span>
                  <span class="info-value" style="text-transform: uppercase; font-weight: bold;">{order_data.payment_method}</span>
                </div>
              </div>
              
              <div class="section">
                <div class="section-title">🛍️ Articles Commandés</div>
                <table>
                  <thead>
                    <tr>
                      <th>Produit</th>
                      <th style="text-align: center;">Qté</th>
                      <th style="text-align: right;">Prix Unit.</th>
                      <th style="text-align: right;">Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {items_html}
                    <tr class="total-row">
                      <td colspan="3" style="text-align: right;">TOTAL À PAYER:</td>
                      <td style="text-align: right;">{order_data.total_amount:,.0f} FCFA</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              
              <div class="section">
                <div class="section-title">⏰ Date de commande</div>
                <p style="margin: 10px 0; color: #666;">{datetime.now().strftime("%d/%m/%Y à %H:%M")}</p>
              </div>
              
              <div style="background-color: #FFF8E7; padding: 15px; border-left: 4px solid #C08831; margin-top: 20px;">
                <p style="margin: 0; color: #995A46;">
                  <strong>Action requise:</strong> Connectez-vous à votre dashboard pour valider cette commande et mettre à jour son statut.
                </p>
              </div>
            </div>
            
            <div class="footer">
              <p style="margin: 0 0 10px 0; font-size: 16px; font-weight: bold;">SOUTOURA_KS</p>
              <p style="margin: 0; font-size: 12px; opacity: 0.8;">Mode Africaine de Luxe</p>
              <p style="margin: 10px 0 0 0; font-size: 11px; opacity: 0.7;">
                Cet email a été envoyé automatiquement. Ne pas répondre.
              </p>
            </div>
          </div>
        </body>
        </html>
        """
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.brevo.com/v3/smtp/email",
                headers={
                    "Content-Type": "application/json",
                    "api-key": BREVO_API_KEY
                },
                json={
                    "sender": {"email": "diallo30amadoukorka@gmail.com", "name": "SOUTOURA_KS"},
                    "to": [{"email": OWNER_EMAIL, "name": "Propriétaire SOUTOURA_KS"}],
                    "subject": f"🛍️ Nouvelle commande #{db_order.id} - SOUTOURA_KS",
                    "htmlContent": email_content
                }
            )
            
            if response.status_code != 201:
                print(f"[Backend] Brevo API error: {response.text}")
            else:
                print(f"[Backend] Email sent successfully to {OWNER_EMAIL}")
                
    except Exception as e:
        print(f"[Backend] Error sending email: {str(e)}")
        # Continue even if email fails
    
    return {"orderId": db_order.id}

@router.patch("/{order_id}", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db)
):
    """Update order status"""
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    if order_update.status:
        db_order.status = order_update.status
    
    db.commit()
    db.refresh(db_order)
    return db_order
