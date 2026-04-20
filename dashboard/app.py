import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

# Configurações de Design
PURPLE_SCALE = "Purples"
FONT_COLOR = "#1f1f1f"
FONT_SIZE = 14

DB_PATH = "C:/Users/rubia/OneDrive/Área de Trabalho/Projeto/Entertainement/entertainment-data-pipeline/data/entertainment.duckdb"

st.set_page_config(page_title="Entertainment Pipeline",
                   layout="wide", page_icon="🎬")

st.markdown(f"""
    <style>
        .block-container {{ padding-top: 2rem; }}
        h1, h2, h3, h4 {{ color: #4B0082; font-weight: 700; }}
    </style>
""", unsafe_allow_html=True)

st.title("🎬 Entertainment Data Pipeline")


def apply_chart_layout(fig):
    fig.update_layout(
        coloraxis_showscale=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=FONT_SIZE, color=FONT_COLOR),
        xaxis=dict(
            showgrid=True,
            gridcolor="#f0f0f0",
            title_font=dict(size=FONT_SIZE, color=FONT_COLOR),
            tickfont=dict(size=FONT_SIZE, color=FONT_COLOR)
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(size=FONT_SIZE, color=FONT_COLOR)
        ),
        margin=dict(l=10, r=100, t=20, b=20),
        height=450,
    )
    return fig


try:
    con = duckdb.connect(DB_PATH, read_only=True)
    tab1, tab2 = st.tabs(["🎥 Filmes", "🎵 Músicas"])

    with tab1:
        st.subheader("Top 5 filmes com maior nota média (últimos 30 dias)")
        top_movies = con.execute('''
            SELECT title, 
                   MAX(CAST(vote_average AS DOUBLE)) as vote_average,
                   MAX(CAST(vote_count AS INTEGER)) as vote_count
            FROM stg_movies
            WHERE CAST(release_date AS DATE) >= CURRENT_DATE - INTERVAL 30 DAYS
            GROUP BY title
            ORDER BY vote_average DESC, vote_count DESC
            LIMIT 5
        ''').df()

        if not top_movies.empty:
            top_movies = top_movies.sort_values("vote_average", ascending=True)
            fig = px.bar(
                top_movies,
                x="vote_average",
                y="title",
                orientation="h",
                color="vote_average",
                color_continuous_scale=PURPLE_SCALE,
                # Adicionamos a tradução de vote_count aqui:
                labels={
                    "vote_average": "Nota média",
                    "title": "Filme",
                    "vote_count": "Contagem de votos"
                },
                text="vote_average",
                hover_name="title",
                hover_data={"title": False,
                            "vote_average": ":.2f", "vote_count": True}
            )
            fig.update_traces(
                texttemplate="<b>%{text:.1f}</b>", textposition="outside")
            st.plotly_chart(apply_chart_layout(fig), use_container_width=True)

    with tab2:
        st.subheader("Top 10 artistas do gênero K-Pop")
        artists = con.execute('''
            SELECT artist_name, listeners_brazil, listeners_global, ontour, tags
            FROM top10_brazil_artists
            WHERE list_contains(tags, 'k-pop') OR list_contains(tags, 'kpop')
            ORDER BY listeners_brazil DESC
            LIMIT 10
        ''').df()

        if not artists.empty:
            # Gráfico de ouvintes no Brasil
            st.markdown("#### Ouvintes no Brasil")
            fig_brazil = px.bar(
                artists.sort_values("listeners_brazil", ascending=True),
                x="listeners_brazil",
                y="artist_name",
                orientation="h",
                color="listeners_brazil",
                color_continuous_scale=PURPLE_SCALE,
                text="listeners_brazil",
                # Renomeando campos nos eixos
                labels={"listeners_brazil": "Ouvintes no Brasil",
                        "artist_name": "Nome do artista"}
            )
            fig_brazil.update_traces(
                texttemplate="<b>%{text:,.0f}</b>", textposition="outside")
            st.plotly_chart(apply_chart_layout(fig_brazil),
                            use_container_width=True)

            st.divider()

            # Gráfico de ouvintes globais
            st.markdown("#### Ouvintes Globais")
            fig_global = px.bar(
                artists.sort_values("listeners_global", ascending=True),
                x="listeners_global",
                y="artist_name",
                orientation="h",
                color="listeners_global",
                color_continuous_scale=PURPLE_SCALE,
                text="listeners_global",
                # Renomeando campos nos eixos
                labels={"listeners_global": "Ouvintes globais",
                        "artist_name": "Nome do artista"}
            )
            fig_global.update_traces(
                texttemplate="<b>%{text:,.0f}</b>", textposition="outside")
            st.plotly_chart(apply_chart_layout(fig_global),
                            use_container_width=True)

finally:
    con.close()
