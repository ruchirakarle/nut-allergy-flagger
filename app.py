import streamlit as st

from nutlogic import check

st.set_page_config(page_title="Nut Flagger", page_icon="🥜", layout="centered")

st.markdown(
    """
<style>
.stApp { background: linear-gradient(160deg, #fff6e5 0%, #ffe3ec 100%); }
h1, h2, h3, p, label, .stMarkdown { font-family: "Trebuchet MS", "Comic Sans MS", sans-serif; }
.title { text-align:center; font-size:3rem; font-weight:800; color:#8a4b1f; margin-bottom:0; }
.sub { text-align:center; color:#a0643a; margin-bottom:1.5rem; }
.card { border-radius:24px; padding:1.4rem 1.6rem; margin-top:1rem; text-align:center;
        box-shadow:0 6px 18px rgba(138,75,31,.15); }
.card .big { font-size:3.2rem; line-height:1; }
.card h2 { margin:.4rem 0 .2rem; }
.bad  { background:#ffd9d4; color:#8c1d12; }
.warn { background:#fff0b8; color:#7a5a00; }
.good { background:#d6f5d6; color:#1d6a2a; }
.chip { display:inline-block; margin:.2rem; padding:.25rem .8rem; border-radius:999px;
        background:rgba(255,255,255,.75); font-weight:700; }
.fine { text-align:center; color:#a0643a; font-size:.8rem; margin-top:2rem; }
</style>
<div class="title">🥜 Nut Flagger 🌰</div>
<div class="sub">Paste an ingredient list and I'll sniff out nuts for you!</div>
""",
    unsafe_allow_html=True,
)

EXAMPLES = {
    "🍫 Choco spread": "Sugar, palm oil, hazelnuts (13%), skimmed milk powder, cocoa, soy lecithin, vanillin.",
    "🥣 Oat cereal": "Whole grain oats, sugar, honey, salt. May contain traces of tree nuts.",
    "🍞 Plain bread": "Wheat flour, water, yeast, salt, sugar, sunflower oil.",
    "🥥 Tricky one": "Coconut milk, nutmeg, butternut squash, sea salt.",
}

if "text" not in st.session_state:
    st.session_state.text = ""

st.write("**Try an example:**")
cols = st.columns(len(EXAMPLES))
for col, (label, txt) in zip(cols, EXAMPLES.items()):
    if col.button(label, use_container_width=True):
        st.session_state.text = txt

text = st.text_area(
    "Ingredients",
    key="text",
    height=140,
    placeholder="e.g. Sugar, almonds, cocoa butter, milk powder...",
)

if st.button("🔍 Check for nuts", type="primary", use_container_width=True):
    if not text.strip():
        st.info("Type or paste some ingredients first! 🐿️")
    else:
        r = check(text)
        found = lambda ws: "".join(f'<span class="chip">{w}</span>' for w in ws)
        if r.status == "contains":
            chips = ""
            if r.tree_nuts:
                chips += "<div>🌰 Tree nuts: " + found(r.tree_nuts) + "</div>"
            if r.peanuts:
                chips += "<div>🥜 Peanuts: " + found(r.peanuts) + "</div>"
            note = (
                "<p>Pine nuts are technically seeds, but they trigger some nut allergies.</p>"
                if r.pine_only
                else ""
            )
            st.markdown(
                f'<div class="card bad"><div class="big">🚫</div>'
                f"<h2>Contains nuts!</h2>{chips}{note}</div>",
                unsafe_allow_html=True,
            )
        elif r.status == "may_contain":
            st.markdown(
                f'<div class="card warn"><div class="big">⚠️</div>'
                f"<h2>May contain traces</h2>"
                f"<div>Warning mentions: {found(r.traces)}</div>"
                f"<p>Made in a shared facility. Risky if your allergy is severe.</p></div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="card good"><div class="big">✅</div>'
                "<h2>No nuts spotted</h2>"
                "<p>I didn't find any nut words in this list.</p></div>",
                unsafe_allow_html=True,
            )

st.markdown(
    '<div class="fine">Demo only, based on simple keyword matching (about 97% of nut products caught in testing). '
    "Always read the real label and ask a doctor if you have a serious allergy. 💛</div>",
    unsafe_allow_html=True,
)
