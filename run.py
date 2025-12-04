import streamlit as st

# -------------------------------
# Configuration générale
# -------------------------------
st.set_page_config(
    page_title="Boutique Fashion Luxe",
    page_icon="🛍️",
    layout="wide"
)

# -------------------------------
# CSS PERSONNALISÉ (Design premium)
# -------------------------------
custom_css = """
<style>

body {
    background: linear-gradient(120deg, #1a1a1a, #0d0d0d);
}

/* TITRES */
h1, h2, h3 {
    font-family: 'Poppins', sans-serif;
    color: white;
}

/* CARTES PRODUITS */
.product-card {
    background: #ffffff10;
    backdrop-filter: blur(10px);
    padding: 18px;
    border-radius: 16px;
    transition: 0.25s;
    border: 1px solid #ffffff20;
}

.product-card:hover {
    transform: scale(1.03);
    background: #ffffff15;
    border-color: #ffffff40;
    cursor: pointer;
}

/* IMAGES */
.product-img {
    border-radius: 12px;
    width: 100%;
    object-fit: cover;
    box-shadow: 0px 4px 16px #00000040;
}

/* BOUTONS */
.stButton>button {
    width: 100%;
    border-radius: 50px;
    padding: 10px;
    background: linear-gradient(90deg, #ff6b6b, #f06595);
    color: white;
    font-weight: 600;
    border: none;
    transition: 0.3s;
}

.stButton>button:hover {
    background: linear-gradient(90deg, #ff8787, #f783ac);
    transform: scale(1.05);
}

</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# -------------------------------
# HEADER / HERO BANNER
# -------------------------------
st.markdown("""
<div style="
    text-align:center;
    padding: 40px 10px;
">
    <h1 style="font-size: 60px; margin-bottom:-5px;">FASHION LUXE</h1>
    <h3 style="opacity:0.8;">La boutique élégante & moderne</h3>
</div>
""", unsafe_allow_html=True)

# -------------------------------
# LISTE DES PRODUITS (exemple)
# -------------------------------

products = [
    {
        "name": "Veste Oversize Premium",
        "price": 79.99,
        "img": "https://images.unsplash.com/photo-1544441893-675973e31985?q=80&w=800"
    },
    {
        "name": "T-shirt Essentials",
        "price": 24.99,
        "img": "https://images.unsplash.com/photo-1593032457860-9b3a7e9a0c8f?q=80&w=800"
    },
    {
        "name": "Pantalon Cargo Urban",
        "price": 59.99,
        "img": "https://images.unsplash.com/photo-1602810318383-e6e7c7ec52b4?q=80&w=800"
    },
    {
        "name": "Sweat Minimaliste Premium",
        "price": 49.99,
        "img": "https://images.unsplash.com/photo-1549298916-b41d501d3772?q=80&w=800"
    },
    {
        "name": "Robe Élégante Soirée",
        "price": 89.99,
        "img": "https://images.unsplash.com/photo-1520975922031-aeec6eb8b402?q=80&w=800"
    },
    {
        "name": "Chemise Classique Homme",
        "price": 39.99,
        "img": "https://images.unsplash.com/photo-1523664234231-2e1d9b90f3df?q=80&w=800"
    },
]

# -------------------------------
# GRID PRODUITS
# -------------------------------
cols = st.columns(3)

for i, product in enumerate(products):
    col = cols[i % 3]

    with col:
        st.markdown(f"""
        <div class="product-card">
            <img src="{product['img']}" class="product-img" />
            <h3 style="margin-top:15px;">{product['name']}</h3>
            <p style="color:#ffdddd; font-size:20px; font-weight:600;">
                {product['price']} €
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.button("Ajouter au panier", key=product["name"])

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("""
<br><br>
<div style="text-align:center; opacity:0.5; padding:20px;">
    <p>© 2025 FASHION LUXE — Créé avec ❤️ en Streamlit</p>
</div>
""", unsafe_allow_html=True)
