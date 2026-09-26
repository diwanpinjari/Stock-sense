import os

def create_file(path, raw_text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    clean_text = raw_text.replace("__LT__", "<").replace("__GT__", ">").strip()
    with open(path, "w", encoding="utf-8") as f:
        f.write(clean_text)
    print(f"Generated: {path}")

LANDING_HTML = """
__LT__!DOCTYPE html__GT__
__LT__html lang="en"__GT__
__LT__head__GT__
    __LT__meta charset="UTF-8"__GT__
    __LT__meta name="viewport" content="width=device-width, initial-scale=1.0"__GT__
    __LT__title__GT__StockSense - Double-Entry Inventory Management System__LT__/title__GT__
    __LT__style__GT__
        :root {
            --primary: #714B67;
            --primary-dark: #53334b;
            --primary-light: #fbf5fa;
            --secondary: #017E84;
            --text-dark: #0f172a;
            --text-muted: #64748b;
            --bg-light: #f8fafc;
            --border: #e2e8f0;
            --accent-green: #10b981;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: var(--bg-light); color: var(--text-dark); line-height: 1.6; }
        
        /* Navbar */
        nav { background: #ffffff; border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 100; }
        .nav-container { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding: 16px 24px; }
        .brand { font-size: 1.4rem; font-weight: 800; color: var(--primary); text-decoration: none; display: flex; align-items: center; gap: 8px; }
        .nav-links { display: flex; align-items: center; gap: 20px; list-style: none; }
        .nav-links a { text-decoration: none; color: var(--text-muted); font-weight: 500; font-size: 0.95rem; transition: color 0.15s; }
        .nav-links a:hover { color: var(--primary); }
        
        /* Buttons */
        .btn { display: inline-flex; align-items: center; justify-content: center; padding: 10px 22px; border-radius: 8px; font-size: 0.95rem; font-weight: 600; text-decoration: none; transition: 0.2s; border: none; cursor: pointer; }
        .btn-primary { background: var(--primary); color: #ffffff; }
        .btn-primary:hover { background: var(--primary-dark); }
        .btn-outline { background: transparent; border: 1.5px solid var(--border); color: var(--text-dark); }
        .btn-outline:hover { background: #f1f5f9; }
        
        /* Hero Section */
        .hero { max-width: 1200px; margin: 0 auto; padding: 80px 24px 60px; text-align: center; }
        .badge-pill { display: inline-block; padding: 6px 14px; background: var(--primary-light); color: var(--primary); border: 1px solid #ebdce8; border-radius: 9999px; font-size: 0.82rem; font-weight: 700; margin-bottom: 24px; text-transform: uppercase; letter-spacing: 0.05em; }
        .hero h1 { font-size: 3.2rem; font-weight: 800; line-height: 1.15; color: var(--text-dark); max-width: 900px; margin: 0 auto 20px; }
        .hero h1 span { color: var(--primary); }
        .hero p { font-size: 1.2rem; color: var(--text-muted); max-width: 680px; margin: 0 auto 36px; }
        .hero-actions { display: flex; justify-content: center; gap: 16px; margin-bottom: 48px; }
        
        /* Architecture Highlights Banner */
        .tech-banner { max-width: 900px; margin: 0 auto 70px; background: #ffffff; border: 1px solid var(--border); border-radius: 12px; padding: 20px 32px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; text-align: left; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); }
        .tech-item h4 { font-size: 0.95rem; color: var(--text-dark); font-weight: 700; margin-bottom: 4px; }
        .tech-item p { font-size: 0.82rem; color: var(--text-muted); }
        
        /* Feature Grid */
        .features-section { max-width: 1200px; margin: 0 auto; padding: 20px 24px 80px; }
        .section-header { text-align: center; margin-bottom: 48px; }
        .section-header h2 { font-size: 2rem; font-weight: 800; margin-bottom: 12px; }
        .section-header p { color: var(--text-muted); font-size: 1rem; }
        
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 24px; }
        .card { background: #ffffff; border: 1px solid var(--border); border-radius: 12px; padding: 28px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
        .card-icon { width: 44px; height: 44px; border-radius: 8px; background: var(--primary-light); color: var(--primary); display: flex; align-items: center; justify-content: center; font-size: 1.3rem; margin-bottom: 18px; }
        .card h3 { font-size: 1.15rem; font-weight: 700; margin-bottom: 10px; }
        .card p { font-size: 0.92rem; color: var(--text-muted); }
        
        /* CTA Section */
        .cta-wrap { max-width: 1200px; margin: 0 auto 80px; padding: 0 24px; }
        .cta-card { background: linear-gradient(135deg, var(--primary) 0%, #46253d 100%); color: #ffffff; border-radius: 16px; padding: 50px 32px; text-align: center; }
        .cta-card h2 { font-size: 2.2rem; font-weight: 800; margin-bottom: 14px; }
        .cta-card p { font-size: 1.1rem; opacity: 0.9; margin-bottom: 28px; max-width: 600px; margin-left: auto; margin-right: auto; }
        .btn-white { background: #ffffff; color: var(--primary); font-weight: 700; }
        .btn-white:hover { background: #f8fafc; }
        
        footer { border-top: 1px solid var(--border); padding: 32px 24px; text-align: center; color: var(--text-muted); font-size: 0.88rem; background: #ffffff; }
    __LT__/style__GT__
__LT__/head__GT__
__LT__body__GT__
    __LT__nav__GT__
        __LT__div class="nav-container"__GT__
            __LT__a href="{% url 'home' %}" class="brand"__GT__📦 StockSense__LT__/a__GT__
            __LT__ul class="nav-links"__GT__
                __LT__li__GT____LT__a href="#features"__GT__Features__LT__/a__GT____LT__/li__GT__
                __LT__li__GT____LT__a href="#architecture"__GT__Architecture__LT__/a__GT____LT__/li__GT__
                {% if user.is_authenticated %}
                    __LT__li__GT____LT__a href="{% url 'dashboard' %}" class="btn btn-primary"__GT__Open Dashboard →__LT__/a__GT____LT__/li__GT__
                    __LT__li__GT____LT__a href="{% url 'logout' %}" class="btn btn-outline" style="padding: 8px 16px;"__GT__Logout__LT__/a__GT____LT__/li__GT__
                {% else %}
                    __LT__li__GT____LT__a href="{% url 'login' %}" class="btn btn-outline"__GT__Sign In__LT__/a__GT____LT__/li__GT__
                    __LT__li__GT____LT__a href="{% url 'register' %}" class="btn btn-primary"__GT__Register Account__LT__/a__GT____LT__/li__GT__
                {% endif %}
            __LT__/ul__GT__
        __LT__/div__GT__
    __LT__/nav__GT__

    __LT__section class="hero"__GT__
        __LT__div class="badge-pill"__GT__Odoo Hackathon 2026 Edition__LT__/div__GT__
        __LT__h1__GT__Modular Inventory Management with __LT__span__GT__Double-Entry Ledger__LT__/span__GT____LT__/h1__GT__
        __LT__p__GT__
            High-integrity inventory engine built with Django and dynamic SQLite. Tracks incoming vendor receipts, customer deliveries, internal transfers, and reconciliations with zero cloud lock-in.
        __LT__/p__GT__
        __LT__div class="hero-actions"__GT__
            {% if user.is_authenticated %}
                __LT__a href="{% url 'dashboard' %}" class="btn btn-primary" style="font-size: 1.05rem; padding: 12px 28px;"__GT__Enter Workspace Dashboard →__LT__/a__GT__
            {% else %}
                __LT__a href="{% url 'register' %}" class="btn btn-primary" style="font-size: 1.05rem; padding: 12px 28px;"__GT__Create Free Account__LT__/a__GT__
                __LT__a href="{% url 'login' %}" class="btn btn-outline" style="font-size: 1.05rem; padding: 12px 28px;"__GT__Sign In__LT__/a__GT__
            {% endif %}
        __LT__/div__GT__

        __LT__div class="tech-banner" id="architecture"__GT__
            __LT__div class="tech-item"__GT__
                __LT__h4__GT__Double-Entry Ledger__LT__/h4__GT__
                __LT__p__GT__Every physical move writes an immutable debit & credit audit record.__LT__/p__GT__
            __LT__/div__GT__
            __LT__div class="tech-item"__GT__
                __LT__h4__GT__Zero Negative Stock__LT__/h4__GT__
                __LT__p__GT__Service layer validation prevents unverified dispatches before posting.__LT__/p__GT__
            __LT__/div__GT__
            __LT__div class="tech-item"__GT__
                __LT__h4__GT__Console OTP Security__LT__/h4__GT__
                __LT__p__GT__Terminal-based verification codes for rapid developer verification.__LT__/p__GT__
            __LT__/div__GT__
        __LT__/div__GT__
    __LT__/section__GT__

    __LT__section class="features-section" id="features"__GT__
        __LT__div class="section-header"__GT__
            __LT__h2__GT__Core Operational Workflows__LT__/h2__GT__
            __LT__p__GT__End-to-end database-driven operations engineered for real warehouse requirements.__LT__/p__GT__
        __LT__/div__GT__

        __LT__div class="grid"__GT__
            __LT__div class="card"__GT__
                __LT__div class="card-icon"__GT__📥__LT__/div__GT__
                __LT__h3__GT__Vendor Receipts__LT__/h3__GT__
                __LT__p__GT__Log incoming shipments from suppliers, verify item quantities, and automatically increase stock balances in storage bins upon validation.__LT__/p__GT__
            __LT__/div__GT__
            __LT__div class="card"__GT__
                __LT__div class="card-icon"__GT__📤__LT__/div__GT__
                __LT__h3__GT__Customer Deliveries__LT__/h3__GT__
                __LT__p__GT__Pick and pack outgoing goods. Embedded atomic locks inspect available inventory to prevent dispatching stock that does not exist.__LT__/p__GT__
            __LT__/div__GT__
            __LT__div class="card"__GT__
                __LT__div class="card-icon"__GT__🔄__LT__/div__GT__
                __LT__h3__GT__Internal Relocations__LT__/h3__GT__
                __LT__p__GT__Move raw materials and finished goods between production racks, aisles, and separate warehouse facilities with live tracking.__LT__/p__GT__
            __LT__/div__GT__
            __LT__div class="card"__GT__
                __LT__div class="card-icon"__GT__⚖️__LT__/div__GT__
                __LT__h3__GT__Discrepancy Adjustments__LT__/h3__GT__
                __LT__p__GT__Reconcile physical floor counts with system balances. System automatically logs gains or losses to an inventory adjustment account.__LT__/p__GT__
            __LT__/div__GT__
            __LT__div class="card"__GT__
                __LT__div class="card-icon"__GT__📊__LT__/div__GT__
                __LT__h3__GT__Executive Dashboard__LT__/h3__GT__
                __LT__p__GT__Real-time KPIs displaying total catalog size, unit counts, low-stock reorder triggers, and active pending operational queues.__LT__/p__GT__
            __LT__/div__GT__
            __LT__div class="card"__GT__
                __LT__div class="card-icon"__GT__📜__LT__/div__GT__
                __LT__h3__GT__Stock Ledger Audit__LT__/h3__GT__
                __LT__p__GT__Complete compliance trail showing timestamp, operator, source, destination, and product movement history for every transaction.__LT__/p__GT__
            __LT__/div__GT__
        __LT__/div__GT__
    __LT__/section__GT__

    __LT__div class="cta-wrap"__GT__
        __LT__div class="cta-card"__GT__
            __LT__h2__GT__Ready to Manage Your Warehouse?__LT__/h2__GT__
            __LT__p__GT__Sign in to start receiving inventory, processing customer dispatches, and reviewing stock health.__LT__/p__GT__
            {% if user.is_authenticated %}
                __LT__a href="{% url 'dashboard' %}" class="btn btn-white" style="padding: 12px 28px;"__GT__Go to Dashboard →__LT__/a__GT__
            {% else %}
                __LT__a href="{% url 'register' %}" class="btn btn-white" style="padding: 12px 28px;"__GT__Get Started Now__LT__/a__GT__
            {% endif %}
        __LT__/div__GT__
    __LT__/div__GT__

    __LT__footer__GT__
        __LT__p__GT__StockSense © 2026. Built for Odoo Hackathon. Powered by Django & SQLite.__LT__/p__GT__
    __LT__/footer__GT__
__LT__/body__GT__
__LT__/html__GT__
"""

create_file("templates/landing.html", LANDING_HTML)
print("SUCCESS: Landing page generated cleanly!")