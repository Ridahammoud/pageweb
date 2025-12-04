import streamlit as st
from pathlib import Path
import re
import random
import os
import base64
import json

# ============================================================
# CONFIG GÉNÉRALE
# ============================================================
st.set_page_config(
    page_title="Parfumerie Luxe",
    page_icon="🛍️",
    layout="wide",
)

# ============================================================
# CHARGEMENT DES IMAGES & CONSTRUCTION DES PRODUITS
# ============================================================

BASE_IMG_DIR = Path(__file__).parent / "images"
pattern = r"IMG-20251012-WA(\d{4})\.jpg"

# Catégories principales façon parfumerie
CATEGORY_CYCLE = ["Parfum", "Coffrets", "Maquillage", "Soins visage", "Soins corps"]

BADGE_TYPES = ["Nouveau", "Promo", "Édition limitée", None]

PRODUCTS = []

files = sorted(BASE_IMG_DIR.glob("IMG-20251012-WA*.jpg"))
for idx, file in enumerate(files, start=1):
    match = re.match(pattern, file.name)
    if match:
        number = int(match.group(1))
    else:
        number = idx

    category = CATEGORY_CYCLE[(idx - 1) % len(CATEGORY_CYCLE)]
    badge = BADGE_TYPES[(idx - 1) % len(BADGE_TYPES)]

    PRODUCTS.append(
        {
            "id": number,
            "name": f"Parfum d'exception {number}",
            "brand": "Marque de luxe",
            "price": round(random.uniform(39, 159), 2),
            "category": category,
            "badge": badge,
            "image": str(file),
            "description": "Un parfum raffiné aux notes élégantes, idéal pour les grandes occasions.",
        }
    )

PRODUCTS = sorted(PRODUCTS, key=lambda x: x["id"])
CATEGORIES = ["Tous"] + sorted(list({p["category"] for p in PRODUCTS}))

# ============================================================
# OPTIONNEL : ENRICHIR AVEC L'IA (marque / nom / description)
# ============================================================

def enrich_products_with_ai(products):
    """
    Optionnel : si OPENAI_API_KEY est défini, on utilise l’IA pour
    détecter la marque et le nom du parfum à partir de l’image.

    Pour activer :
      pip install openai
      export OPENAI_API_KEY="ta_clé"
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return products

    try:
        from openai import OpenAI
    except ImportError:
        return products

    client = OpenAI(api_key=api_key)

    for p in products:
        img_path = p["image"]
        try:
            with open(img_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")

            prompt = (
                "Tu es un expert parfumerie. À partir de cette photo de boîte de parfum, "
                "détecte : 1) la marque, 2) le nom du parfum, 3) un court texte marketing. "
                "Répond STRICTEMENT au format JSON : "
                '{"brand": "...", "name": "...", "description": "..."}'
            )

            resp = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "Assistant parfumerie."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "input_image",
                                "image_url": f"data:image/jpeg;base64,{b64}",
                            },
                        ],
                    },
                ],
            )

            txt = resp.choices[0].message.content
            data = json.loads(txt)

            p["brand"] = data.get("brand", p["brand"])
            p["name"] = data.get("name", p["name"])
            p["description"] = data.get("description", p["description"])

        except Exception:
            # en cas d’erreur on garde les valeurs par défaut
            continue

    return products


# Décommente la ligne suivante si tu veux vraiment enrichir via IA
# PRODUCTS = enrich_products_with_ai(PRODUCTS)


# ============================================================
# SESSION STATE
# ============================================================

def init_session():
    ss = st.session_state
    if "page" not in ss:
        ss.page = "Accueil"
    if "logged_in" not in ss:
        ss.logged_in = False
    if "username" not in ss:
        ss.username = ""
    if "cart" not in ss:
        ss.cart = {}
    if "selected_product_id" not in ss:
        ss.selected_product_id = None
    if "current_category" not in ss:
        ss.current_category = "Tous"
    if "search_query" not in ss:
        ss.search_query = ""
    if "carousel_offset" not in ss:
        ss.carousel_offset = 0


init_session()

# ============================================================
# THEME & CSS STYLE PARFUMERIE
# ============================================================

def render_css():
    css = """
    <style>
    .main, body {
        background: #F4F2F7 !important;
        font-family: 'Poppins', sans-serif;
    }

    /* NAVBAR HAUTE */
    .top-nav {
        width: 100%;
        background: #ffffff;
        border-bottom: 1px solid #e5e5e5;
        padding: 16px 30px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: sticky;
        top: 0;
        z-index: 999;
    }

    .brand-title {
        font-size: 24px;
        font-weight: 800;
        color: #4A148C !important;
        letter-spacing: 1px;
    }

    .nav-icons {
        display: flex;
        gap: 18px;
        font-size: 18px;
    }

    /* BARRE DE RECHERCHE */
    .search-wrapper {
        background: #ffffff;
        padding: 18px 40px 10px 40px;
        border-bottom: 1px solid #e5e5e5;
    }

    .category-bar {
        background: #ffffff;
        padding: 8px 40px 12px 40px;
        border-bottom: 1px solid #e5e5e5;
        display: flex;
        gap: 30px;
        font-size: 14px;
        font-weight: 600;
    }

    .stTextInput>div>div>input {
        border-radius: 999px;
        padding: 10px 18px;
        border: 1px solid #d2cfe3;
    }

    /* MENU CATÉGORIES – boutons arrangés */
    .stButton>button {
        border-radius: 999px;
        padding: 6px 14px;
        border: none;
        background: none;
        color: #444 !important;
        font-weight: 600;
        box-shadow: none;
    }
    .stButton>button:hover {
        color: #7b2cbf !important;
        background: #f4ecff;
    }

    /* Bouton catégorie actif */
    .category-active>button {
        color: #ffffff !important;
        background: #e91e63 !important;
    }

    /* TITRE SECTION */
    .section-title {
        font-size: 26px;
        font-weight: 700;
        text-align: center;
        margin: 25px 0 15px 0;
    }

    /* CARTE PRODUIT */
    .product-card {
        background: #ffffff;
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
        height: 260px;
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
        font-size: 15px;
        font-weight: 600;
        color: #333;
        margin-bottom: 4px;
    }
    .product-price {
        font-size: 20px;
        font-weight: 800;
        color: #000;
        margin-top: 10px;
    }

    /* BADGES */
    .badge {
        background: #ffffff;
        border: 1px solid #000000;
        color: #000000;
        display: inline-block;
        padding: 4px 8px;
        font-size: 11px;
        font-weight: 600;
        margin-bottom: 8px;
        border-radius: 4px;
    }

    /* BOUTONS ACTION (Ajouter / Voir) */
    .action-btn>button {
        background: #7b2cbf !important;
        color: #ffffff !important;
        padding: 6px 16px;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    }
    .action-btn>button:hover {
        background: #5a189a !important;
        transform: translateY(-2px);
    }

    /* PAGE PRODUIT */
    .product-page-title {
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .product-page-brand {
        font-size: 14px;
        font-weight: 700;
        color: #7b2cbf;
    }
    .product-page-price {
        font-size: 26px;
        font-weight: 800;
        margin: 10px 0 16px 0;
    }

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


render_css()

# ============================================================
# UTILITAIRES
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


def set_page(page: str):
    st.session_state.page = page


# ============================================================
# HEADER / NAVIGATION
# ============================================================

def render_header():
    # Bandeau supérieur
    st.markdown(
        """
        <div class="top-nav">
            <div class="brand-title">Parfumerie Luxe</div>
            <div class="nav-icons">
                <span>❤️</span>
                <span>👤</span>
                <span>🛒</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Barre de recherche
    with st.container():
        st.markdown('<div class="search-wrapper">', unsafe_allow_html=True)
        st.session_state.search_query = st.text_input(
            "Rechercher un produit",
            value=st.session_state.search_query,
            placeholder="Rechercher un parfum, une marque, une gamme...",
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # Menu catégories façon parfumerie
    st.markdown('<div class="category-bar">', unsafe_allow_html=True)
    cols = st.columns(len(CATEGORIES))
    for i, cat in enumerate(CATEGORIES):
        key = f"cat_{cat}"
        css_class = "category-active" if st.session_state.current_category == cat else ""
        with cols[i]:
            st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
            if st.button(cat.upper(), key=key):
                st.session_state.current_category = cat
                set_page("Boutique")
            st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# PAGES
# ============================================================

def page_home():
    st.markdown('<div class="section-title">Bienvenue dans votre parfumerie en ligne</div>', unsafe_allow_html=True)
    st.write(
        "Découvrez une sélection de parfums de créateurs, coffrets cadeaux et soins d’exception, "
        "livrés rapidement depuis nos stocks."
    )
    st.write("")
    if st.button("Découvrir la boutique 🧴"):
        set_page("Boutique")


def filtered_products():
    """Applique recherche + catégorie."""
    prods = PRODUCTS

    # Catégorie
    cat = st.session_state.current_category
    if cat != "Tous":
        prods = [p for p in prods if p["category"] == cat]

    # Recherche
    q = st.session_state.search_query.strip().lower()
    if q:
        prods = [
            p
            for p in prods
            if q in p["name"].lower() or q in p["brand"].lower() or q in p["category"].lower()
        ]

    return prods


def page_shop():
    st.markdown('<div class="section-title">Notre sélection</div>', unsafe_allow_html=True)

    prods = filtered_products()
    if not prods:
        st.info("Aucun produit ne correspond à votre recherche pour le moment.")
        return

    cols = st.columns(4)
    for i, product in enumerate(prods):
        col = cols[i % 4]
        with col:
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            # badge
            if product.get("badge"):
                st.markdown(f"<div class='badge'>{product['badge']}</div>", unsafe_allow_html=True)
            st.image(product["image"])
            st.markdown(
                f"<div class='product-brand'>{product['brand']}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='product-name'>{product['name']}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='product-price'>{product['price']:.2f} €</div>",
                unsafe_allow_html=True,
            )

            b1, b2 = st.columns(2)
            with b1:
                st.markdown('<div class="action-btn">', unsafe_allow_html=True)
                if st.button("Voir", key=f"view_{product['id']}"):
                    st.session_state.selected_product_id = product["id"]
                    set_page("Produit")
                st.markdown("</div>", unsafe_allow_html=True)
            with b2:
                st.markdown('<div class="action-btn">', unsafe_allow_html=True)
                if st.button("Ajouter", key=f"add_{product['id']}"):
                    add_to_cart(product["id"])
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)


def page_product():
    pid = st.session_state.selected_product_id
    product = get_product(pid)
    if not product:
        st.warning("Aucun produit sélectionné.")
        if st.button("Retour à la boutique"):
            set_page("Boutique")
        return

    col_img, col_info = st.columns([2, 3])
    with col_img:
        st.image(product["image"])
    with col_info:
        st.markdown(
            f"<div class='product-page-brand'>{product['brand']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='product-page-title'>{product['name']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='product-page-price'>{product['price']:.2f} €</div>",
            unsafe_allow_html=True,
        )
        if product.get("badge"):
            st.markdown(f"<div class='badge'>{product['badge']}</div>", unsafe_allow_html=True)
        st.write(product["description"])
        st.write("")
        if st.button("Ajouter au panier 🛒"):
            add_to_cart(product["id"])

    st.markdown("### Vous aimerez aussi")

    # Petit carrousel horizontal : 4 produits, avec navigation
    n = len(PRODUCTS)
    offset = st.session_state.carousel_offset
    start = offset % n
    subset = []
    for i in range(4):
        subset.append(PRODUCTS[(start + i) % n])

    cprev, cnext = st.columns([1, 1])
    with cprev:
        if st.button("◀", key="car_prev"):
            st.session_state.carousel_offset = (offset - 1) % n
    with cnext:
        if st.button("▶", key="car_next"):
            st.session_state.carousel_offset = (offset + 1) % n

    cols = st.columns(4)
    for i, p in enumerate(subset):
        with cols[i]:
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            st.image(p["image"])
            st.markdown(
                f"<div class='product-brand'>{p['brand']}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='product-name'>{p['name']}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='product-price'>{p['price']:.2f} €</div>",
                unsafe_allow_html=True,
            )
            if st.button("Voir", key=f"car_view_{p['id']}"):
                st.session_state.selected_product_id = p["id"]
                set_page("Produit")
            st.markdown("</div>", unsafe_allow_html=True)

    if st.button("⬅️ Retour à la boutique"):
        set_page("Boutique")


def page_cart():
    st.markdown('<div class="section-title">Votre panier</div>', unsafe_allow_html=True)

    if not st.session_state.cart:
        st.info("Votre panier est vide.")
        if st.button("Retour à la boutique"):
            set_page("Boutique")
        return

    total = 0.0
    for pid, qty in st.session_state.cart.items():
        p = get_product(pid)
        if not p:
            continue
        line_total = p["price"] * qty
        total += line_total
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            st.write(f"**{p['name']}** ({p['brand']})")
        with c2:
            st.write(f"Quantité : {qty}")
        with c3:
            st.write(f"{line_total:.2f} €")

    st.markdown("---")
    st.write(f"### Total : {total:.2f} €")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Vider le panier"):
            st.session_state.cart = {}
    with c2:
        st.button("Passer la commande ✅", help="Démo – pas de paiement réel.")


def page_account():
    st.markdown('<div class="section-title">Compte</div>', unsafe_allow_html=True)

    if st.session_state.logged_in:
        st.success(f"Connecté en tant que {st.session_state.username}")
        return

    st.info("Connectez-vous pour sauvegarder vos paniers (démonstration).")
    with st.form("login_form"):
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        submitted = st.form_submit_button("Se connecter")
        if submitted:
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
