import streamlit as st
from pathlib import Path
import re
import os
import random

# Dossier images au même niveau que run.py
BASE_IMG_DIR = Path(__file__).resolve().parent / "images"

print("Chemin images :", BASE_IMG_DIR)
print("Existe ? ", BASE_IMG_DIR.exists())
print("Contenu images :", list(BASE_IMG_DIR.glob("*")))

# ============================================================
# CONFIG GÉNÉRALE
# ============================================================
st.set_page_config(
    page_title="Boutique Parfums",
    page_icon="🛍️",
    layout="wide"
)

# ============================================================
# DONNÉES PRODUITS (exemples – adapte à tes images)


BASE_IMG_DIR = Path(__file__).parent / "images"

PRODUCTS = []

# Pattern EXACT correspondant à tes fichiers
pattern = r"IMG-20251012-WA(\d{4})\.jpg"

for file in sorted(BASE_IMG_DIR.iterdir()):
    if file.is_file():
        match = re.match(pattern, file.name)
        if match:
            number = int(match.group(1))  # ex "0046" -> 46

            PRODUCTS.append({
                "id": number,
                "name": f"Parfum {number}",
                "brand": "Marque inconnue",
                "price": round(random.uniform(30, 120), 2),
                "category": "Parfum",
                "image": str(file),
                "description": "Parfum haut de gamme disponible immédiatement."
            })

# Tri final des produits
PRODUCTS = sorted(PRODUCTS, key=lambda x: x["id"])

# Correction : définition des catégories
CATEGORIES = sorted(list({p["category"] for p in PRODUCTS}))


# ============================================================
# INITIALISATION SESSION
# ============================================================

def init_session():
    if "page" not in st.session_state:
        st.session_state.page = "Accueil"
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "cart" not in st.session_state:
        # cart = {product_id: quantity}
        st.session_state.cart = {}
    if "selected_product_id" not in st.session_state:
        st.session_state.selected_product_id = None
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"


init_session()


# ============================================================
# THEME + CSS
# ============================================================

def render_css():
    css = """
    <style>

    /* RESET STREAMLIT BACKGROUND */
    .main, body {
        background: #F4F2F7 !important;
        font-family: 'Poppins', sans-serif;
    }

    /* TOP NAV BAR */
    .top-nav {
        width: 100%;
        background: white;
        border-bottom: 1px solid #e5e5e5;
        padding: 18px 35px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: sticky;
        top: 0;
        z-index: 999;
    }

    .brand-title {
        font-size: 26px;
        font-weight: 700;
        color: #4A148C !important;
        letter-spacing: 1px;
    }

    /* SEARCH BAR */
    .search-container input {
        width: 100%;
        padding: 12px 18px;
        border-radius: 30px;
        border: 1px solid #d2cfe3;
        font-size: 16px;
    }

    /* MENU CATEGORY BAR */
    .category-menu {
        background: white;
        border-bottom: 1px solid #e5e5e5;
        padding: 12px 0;
        display: flex;
        justify-content: center;
        gap: 45px;
        font-size: 15px;
        font-weight: 600;
    }

    .category-menu a {
        text-decoration: none;
        color: #333;
        padding-bottom: 6px;
    }

    .category-menu a:hover {
        color: #7b2cbf;
        border-bottom: 3px solid #7b2cbf;
    }

    /* PRODUCT GRID */
    .product-card {
        background: white;
        border-radius: 10px;
        border: 1px solid #e6e6e6;
        padding: 18px;
        transition: 0.25s ease;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }

    .product-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 4px 18px rgba(0,0,0,0.08);
    }

    .product-card img {
        width: 100%;
        border-radius: 8px;
        object-fit: contain;
        height: 280px;
        background: #fafafa;
        padding: 15px;
        border: 1px solid #f0f0f0;
    }

    .product-brand {
        margin-top: 10px;
        font-size: 13px;
        font-weight: 700;
        color: #7b2cbf;
    }

    .product-name {
        font-size: 16px;
        font-weight: 600;
        color: #333;
        margin-bottom: 6px;
    }

    .product-price {
        font-size: 22px;
        font-weight: 800;
        color: #000;
        margin-top: 10px;
    }

    /* BADGES (NOUVEAU / PROMO) */
    .badge {
        background: white;
        border: 1px solid black;
        color: black;
        display: inline-block;
        padding: 4px 8px;
        font-size: 11px;
        font-weight: 600;
        margin-bottom: 8px;
        border-radius: 4px;
    }

    /* BUTTONS */
    .stButton > button {
        background: #7b2cbf !important;
        color: white !important;
        padding: 10px 22px;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        transition: 0.2s ease;
    }

    .stButton > button:hover {
        background: #5a189a !important;
        transform: translateY(-3px);
    }

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

render_css()


# ============================================================
# HELPERS
# ============================================================

def get_product(pid: int):
    for p in PRODUCTS:
        if p["id"] == pid:
            return p
    return None


def add_to_cart(pid: int):
    cart = st.session_state.cart
    cart[pid] = cart.get(pid, 0) + 1
    st.session_state.cart = cart
    st.toast("Ajouté au panier ✅")


def cart_total():
    total = 0.0
    for pid, qty in st.session_state.cart.items():
        p = get_product(pid)
        if p:
            total += p["price"] * qty
    return total


# ============================================================
# NAVIGATION & HEADER
# ============================================================

def set_page(page_name: str):
    st.session_state.page = page_name


def render_header():
    with st.container():
        st.markdown(
            """
            <div class="top-nav">
                <div>
                    <span class="brand-title">PARFUMERIE LUXE</span><br/>
                    <span class="muted" style="font-size:13px;">Boutique exclusive de parfums de créateurs</span>
                </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            pass

        with col2:
            if st.session_state.logged_in:
                st.write(f"👤 {st.session_state.username}")
                if st.button("Se déconnecter"):
                    st.session_state.logged_in = False
                    st.session_state.username = ""
            else:
                if st.button("Se connecter"):
                    set_page("Compte")

        with col3:
            # Toggle thème
            mode = "🌙 Mode sombre" if st.session_state.theme == "dark" else "☀️ Mode clair"
            if st.button(mode):
                st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
                render_css()

        st.markdown("</div>", unsafe_allow_html=True)

    # Menu simple
    menu_cols = st.columns([1, 1, 1, 1])
    with menu_cols[0]:
        if st.button("🏠 Accueil"):
            set_page("Accueil")
    with menu_cols[1]:
        if st.button("🧴 Boutique"):
            set_page("Boutique")
    with menu_cols[2]:
        if st.button("🛒 Panier"):
            set_page("Panier")
    with menu_cols[3]:
        if st.button("👤 Compte"):
            set_page("Compte")

    st.markdown("---")


# ============================================================
# PAGES
# ============================================================

def page_home():
    left, right = st.columns([3, 2])

    with left:
        st.markdown("### Bienvenue dans")
        st.markdown("## **Parfumerie Luxe**")
        st.markdown(
            '<p class="muted">Découvrez une sélection exclusive de parfums de créateurs, '
            "livrés rapidement depuis nos stocks.</p>",
            unsafe_allow_html=True,
        )
        st.write("")
        st.write("")
        if st.button("Découvrir la boutique 🧴"):
            set_page("Boutique")

    with right:
        st.image(
            "https://images.unsplash.com/photo-1557170334-a9632e77c6e0?q=80&w=1000",
            use_column_width=True,
        )


def page_shop():
    st.subheader("Boutique")

    # Filtres
    with st.expander("🎛️ Filtres", expanded=True):
        col1, col2, col3 = st.columns([2, 2, 2])
        prices = [p["price"] for p in PRODUCTS]
        min_price, max_price = min(prices), max(prices)

        with col1:
            price_range = st.slider(
                "Prix (€)",
                float(min_price),
                float(max_price),
                (float(min_price), float(max_price)),
                step=1.0,
            )

        with col2:
            cat_filter = st.multiselect("Catégories", CATEGORIES, default=CATEGORIES)

        with col3:
            search = st.text_input("Recherche (nom / marque)")

    # Application des filtres
    filtered = []
    for p in PRODUCTS:
        if not (price_range[0] <= p["price"] <= price_range[1]):
            continue
        if p["category"] not in cat_filter:
            continue
        if search:
            if search.lower() not in p["name"].lower() and search.lower() not in p["brand"].lower():
                continue
        filtered.append(p)

    st.markdown("")

    # Grille produits
    cols = st.columns(3)
    for i, product in enumerate(filtered):
        col = cols[i % 3]
        with col:
            with st.container():
                st.markdown('<div class="product-card">', unsafe_allow_html=True)
                st.markdown("<div class='product-card'>", unsafe_allow_html=True)
                st.markdown(f"<span class='badge'>Nouveau</span>", unsafe_allow_html=True)
                st.image(product["image"])
                st.markdown(f"<div class='product-brand'>{product['brand']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='product-name'>{product['name']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='product-price'>{product['price']} €</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown(f"**{product['name']}**")
                st.markdown(f"<span class='muted'>{product['brand']}</span>", unsafe_allow_html=True)
                st.markdown(f"### {product['price']:.2f} €")
                st.markdown(
                    f"<span class='badge'>{product['category']}</span>",
                    unsafe_allow_html=True,
                )

                b1, b2 = st.columns(2)
                with b1:
                    if st.button("Voir", key=f"view_{product['id']}"):
                        st.session_state.selected_product_id = product["id"]
                        set_page("Produit")
                with b2:
                    if st.button("Ajouter 🛒", key=f"add_{product['id']}"):
                        add_to_cart(product["id"])

                st.markdown("</div>", unsafe_allow_html=True)


def page_product():
    pid = st.session_state.selected_product_id
    product = get_product(pid)
    if not product:
        st.warning("Aucun produit sélectionné.")
        if st.button("Retour à la boutique"):
            set_page("Boutique")
        return

    left, right = st.columns([2, 3])

    with left:
        st.image(product["image"], use_column_width=True)
    with right:
        st.markdown(f"#### {product['brand']}")
        st.markdown(f"## **{product['name']}**")
        st.markdown(f"### {product['price']:.2f} €")
        st.markdown(
            f"<span class='badge'>{product['category']}</span>",
            unsafe_allow_html=True,
        )
        st.write("")
        st.write(product["description"])

        st.write("")
        if st.button("Ajouter au panier 🛒"):
            add_to_cart(product["id"])

        st.write("")
        if st.button("⬅️ Retour à la boutique"):
            set_page("Boutique")


def page_cart():
    st.subheader("Votre panier")

    if not st.session_state.cart:
        st.info("Votre panier est vide pour l’instant.")
        if st.button("Aller à la boutique"):
            set_page("Boutique")
        return

    total = 0.0
    for pid, qty in st.session_state.cart.items():
        p = get_product(pid)
        if not p:
            continue
        line_total = p["price"] * qty
        total += line_total
        cols = st.columns([3, 1, 1])
        with cols[0]:
            st.markdown(f"**{p['name']}** ({p['brand']})")
        with cols[1]:
            st.write(f"Quantité : {qty}")
        with cols[2]:
            st.write(f"{line_total:.2f} €")

    st.markdown("---")
    st.markdown(f"### Total : {total:.2f} €")

    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        if st.button("Vider le panier"):
            st.session_state.cart = {}
    with c2:
        st.button("Passer la commande ✅", help="Démo uniquement, pas de paiement réel.")


def page_account():
    st.subheader("Compte utilisateur")

    if st.session_state.logged_in:
        st.success(f"Connecté en tant que {st.session_state.username}")
        st.write("Système de compte simple pour la démo (non sécurisé).")
        return

    st.info("Connecte-toi pour sauvegarder ton panier et tes commandes (démo).")

    with st.form("login_form"):
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        submitted = st.form_submit_button("Se connecter")

        if submitted:
            # Démo : on accepte n'importe quel login si non vide
            if username and password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Connexion réussie ✅")
            else:
                st.error("Merci de remplir les deux champs.")


# ============================================================
# ROUTEUR PRINCIPAL
# ============================================================

def main():
    render_header()

    page = st.session_state.page

    if page == "Accueil":
        page_home()
    elif page == "Boutique":
        page_shop()
    elif page == "Produit":
        page_product()
    elif page == "Panier":
        page_cart()
    elif page == "Compte":
        page_account()
    else:
        page_home()


if __name__ == "__main__":
    main()
