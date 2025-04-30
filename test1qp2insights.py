import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from scipy import stats
import re
from sklearn.feature_extraction.text import CountVectorizer
import textwrap

# --- Helper to sanitize filenames ---
def slugify(text):
    return re.sub(r'[^0-9A-Za-z]+', '_', text).strip('_')

# --- Helper to extract common phrases (bigrams/trigrams) ---
def extract_phrases(texts, top_n=100):
    # Vectorize into 2- and 3-word ngrams, ignoring English stopwords
    vec = CountVectorizer(
        ngram_range=(2,3),
        stop_words='english',
        max_features=top_n
    )
    X = vec.fit_transform(texts)
    # Build a dict of phrase: total_count
    freqs = dict(zip(vec.get_feature_names_out(), X.sum(axis=0).A1))
    return freqs

# --- CONFIGURATION ---
INPUT_CSV = 'QP2 Presentation Peer Evaluation (Responses) - Form Responses 1.csv'
OUTPUT_DIR = 'group_reports'

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- LOAD & PREPARE DATA ---
df = pd.read_csv(INPUT_CSV)
df.columns = [c.strip() for c in df.columns]

# Identify dynamic columns
group_col = 'Presenting Group Number'
cols = df.columns.tolist()
gidx = cols.index(group_col)
# Next 7 are score categories
target_cats = cols[gidx+1 : gidx+1+7]
# Immediately after is feedback column
comment_col = cols[gidx+1+7]

# Calculate group means & percentiles
group_means = df.groupby(group_col)[target_cats].mean()
percentiles = {
    cat: {
        grp: stats.percentileofscore(group_means[cat], group_means.loc[grp, cat])
        for grp in group_means.index
    }
    for cat in target_cats
}

# --- MAIN LOOP: Generate per-group reports ---
for grp, gdf in df.groupby(group_col):
    gslug = slugify(str(grp))
    folder = os.path.join(OUTPUT_DIR, f'group_{gslug}')
    os.makedirs(folder, exist_ok=True)

    # --- 1) High‑DPI Horizontal Boxplots ---
    scores_list = [gdf[cat].dropna().values for cat in target_cats]
    n = len(target_cats)
    # Prepare display labels: shorten one long label, then wrap
    wrapped_labels = []
    for cat in target_cats:
        label = 'Current methods' if cat.lower().startswith('current methods') else cat
        wrapped = textwrap.fill(label, width=25)
        wrapped_labels.append(wrapped)

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)  # Increase width to 16 inches
    bp = ax.boxplot(
        scores_list,
        vert=False,
        patch_artist=True,
        widths=0.6,
        showfliers=False
    )
    ax.set_yticks(np.arange(1, n + 1))
    ax.set_yticklabels(wrapped_labels, fontsize=10)
    ax.set_xlabel('Score', fontsize=12)
    ax.set_ylabel('Categories', fontsize=12, labelpad=20)  # Adjust labelpad
    # Filter the DataFrame for the specific group
    group_data = df[df[group_col] == grp]

    # Calculate the sample size by summing non-NaN values across the target categories
    sample_size = group_data[target_cats].notna().sum().sum()
    #sample_size = sum(len(scores) for scores in scores_list if grp in df[group_col].unique())
    xmin, xmax = ax.get_xlim()
    span = xmax - xmin
    for idx, scores in enumerate(scores_list, start=1):
        mean_val = np.mean(scores)
    sample_size =len(scores)
    # Update the title to include the sample size
    ax.set_title(
        f'Group {grp} Scores by Category (n={sample_size})',
        fontsize=14,
        pad=15)
    ax.grid(axis='x', linestyle='--', alpha=0.5)

    # Rotate x-axis labels if needed
    plt.xticks(rotation=45, ha='right')  # Rotate and align x-axis labels

    fig.tight_layout()  # Ensure everything fits within the figure
    fig.savefig(
        os.path.join(folder, f'{gslug}_horizontal_box.png'),
        dpi=300,
        bbox_inches='tight'
    )
    plt.close(fig)

    # Annotate mean and sample size
    xmin, xmax = ax.get_xlim()
    span = xmax - xmin

    # Annotate percentile further to the right
    for idx, cat in enumerate(target_cats, start=1):
        med = bp['medians'][idx-1].get_xdata().mean()
        pct = percentiles[cat][grp]
        ax.text(
            med + 0.05*span,
            idx,
            f"{pct:.0f}th",
            va='center', ha='left', fontsize=10, fontweight='bold'
        )

    fig.tight_layout()
    fig.savefig(
        os.path.join(folder, f'{gslug}_horizontal_box.png'),
        dpi=300,
        bbox_inches='tight'
    )
    plt.close(fig)

    # --- 2) Phrase‑based Word Cloud ---
    comments = gdf[comment_col].dropna().astype(str).tolist()
    phrase_freq = extract_phrases(comments, top_n=100)
    wc = WordCloud(
        width=800, height=400,
        background_color='white',
        collocations=False
    ).generate_from_frequencies(phrase_freq)
    fig, ax = plt.subplots(figsize=(8,4), dpi=300)
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    ax.set_title(f'Group {grp} Feedback Word Cloud (Phrases)', fontsize=14)
    fig.tight_layout()
    fig.savefig(
        os.path.join(folder, f'{gslug}_phrase_wordcloud.png'),
        dpi=300,
        bbox_inches='tight'
    )
    plt.close(fig)

    # --- 3) Radar Chart of Averages ---
    means = group_means.loc[grp, target_cats].tolist()
    angles = np.linspace(0, 2*np.pi, n, endpoint=False).tolist()
    means += means[:1]
    angles += angles[:1]

    fig = plt.figure(figsize=(6,6), dpi=300)
    ax = fig.add_subplot(111, polar=True)
    ax.plot(angles, means, 'o-', linewidth=2)
    ax.fill(angles, means, alpha=0.25)
    ax.set_thetagrids(np.degrees(angles[:-1]), wrapped_labels, fontsize=9)
    ax.set_title(f'Group {grp} Profile', y=1.08, fontsize=14)
    ax.set_ylim(0, df[target_cats].max().max())
    fig.tight_layout()
    fig.savefig(
        os.path.join(folder, f'{gslug}_radar.png'),
        dpi=300,
        bbox_inches='tight'
    )
    plt.close(fig)

    # 1) Compute ranks (1=highest mean)
    ranks = group_means.rank(ascending=False, axis=0, method='min')

    # 2) Melt to long form
    ranks_long = ranks.reset_index().melt(id_vars=group_col, var_name='Category', value_name='Rank')

    # 3) Plot bump chart
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    for grp in ranks_long[group_col].unique():
        grp_data = ranks_long[ranks_long[group_col] == grp]
        ax.plot(
            grp_data['Category'], grp_data['Rank'],
            marker='o', label=f'Group {grp}', linewidth=2
        )

    ax.invert_yaxis()  # so 1 appears at top
    ax.set_ylabel('Rank (1 = Best)', fontsize=12)
    ax.set_xlabel('Category', fontsize=12)
    ax.set_title('Group Ranking Across Categories', fontsize=14, pad=12)
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Group', bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.tight_layout()
    fig.savefig(os.path.join(folder, f'{gslug}_bump_chart.png'), dpi=300, bbox_inches='tight')
    plt.close(fig)

    # --- Per-Group Comment Buzz Charts ---
    richness = []
    for grp, gdf in df.groupby(group_col):
        # pull all comments for this group
        comments = gdf[comment_col].dropna().astype(str).tolist()
        # keep only comments >3 words AND >=20 characters
        filtered = [c for c in comments if len(c.split()) > 3 and len(c) >= 20]
        # compute metrics
        total_chars = sum(len(c) for c in filtered)
        total_words = sum(len(c.split()) for c in filtered)
        richness.append({'Group': grp, 'Chars': total_chars, 'Words': total_words})

    rich_df = pd.DataFrame(richness).sort_values('Chars', ascending=False).reset_index(drop=True)
    rich_df['Rank'] = rich_df.index + 1
    for _, row in rich_df.iterrows():
        grp = row['Group']
        words = row['Words']
        rank = row['Rank']
        # locate that group's folder
        gslug = slugify(str(grp))
        folder = os.path.join(OUTPUT_DIR, f'group_{gslug}')
        os.makedirs(folder, exist_ok=True)

        fig, ax = plt.subplots(figsize=(6, 2), dpi=300)
        # one horizontal bar
        ax.barh(
            [0],
            [words],
            align='center',
            edgecolor='black',
            height=0.6
        )
        # label on y-axis
        ax.set_yticks([0])
        # ax.set_yticklabels([f'Group {grp}'], fontsize=10)
        ax.set_yticklabels([])
        ax.invert_yaxis()
        # axis and title
        ax.set_xlim(0, rich_df['Words'].max() * 1.1)
        ax.set_xlabel('Total Words in Feedback', fontsize=12)
        ax.set_title(f'Comment Buzz for Group {grp}', fontsize=14, pad=10)
        # in-bar rank annotation
        ax.text(
            x=words * 0.01,
            y=0,
            s=f'Rank #{rank}',
            va='center',
            ha='left',
            fontsize=11,
            color='white'
        )

        plt.tight_layout()
        fig.savefig(
            os.path.join(folder, f'{gslug}_comment_buzz.png'),
            dpi=300, bbox_inches='tight'
        )
        plt.close(fig)

print('All reports generated to:', OUTPUT_DIR)
# --- 5) Summary of Top Groups per Category & Overall ---

# 1) Sum raw scores per group
sum_scores = df.groupby(group_col)[target_cats].sum()

# 2) Best group for each category (highest total)
best_per_cat = sum_scores.idxmax()

# 3) Compute an overall total across all categories
sum_scores['Overall'] = sum_scores.sum(axis=1)
best_overall = sum_scores['Overall'].idxmax()

# 4) Print out the results
print("🏆 Best Group per Category:")
for cat, grp in best_per_cat.items():
    total = sum_scores.loc[grp, cat]
    print(f"  • {cat}: Group {grp} (total = {total:.1f})")

overall_score = sum_scores.loc[best_overall, 'Overall']
print(f"\n🥇 Best Overall Group: Group {best_overall} with total score {overall_score:.1f}")
# --- Full Ranking of All Groups ---

# --- 6) Rankings Adjusted for Response Count ---

# 1) Count respondents per group
response_counts = df.groupby(group_col).size().rename('n_respondents')

# 2) Sum raw scores per group (if not already done)
sum_scores = df.groupby(group_col)[target_cats].sum()

# 3) Compute average score per respondent
avg_scores = sum_scores.div(response_counts, axis=0)

# 4) Print avg-based rankings per category
print("📊 Adjusted Rankings per Category (avg score, n respondents):")
for cat in target_cats:
    print(f"\n› {cat}:")
    ranked = avg_scores[cat].sort_values(ascending=False)
    for i, (grp, avg_sc) in enumerate(ranked.items(), start=1):
        n = response_counts.loc[grp]
        print(f"    {i:>2}. Group {grp} — avg = {avg_sc:.2f} (n={n})")

# 5) Overall average across all categories
avg_scores['Overall'] = avg_scores.mean(axis=1)
print("\n🏅 Overall Adjusted Ranking (avg of all categories):")
overall = avg_scores['Overall'].sort_values(ascending=False)
for i, (grp, avg_all) in enumerate(overall.items(), start=1):
    n = response_counts.loc[grp]
    print(f"    {i:>2}. Group {grp} — avg = {avg_all:.2f} (n={n})")

# --- Top Group per Category After Adjustment ---
print("🏆 Top Group per Category (Adjusted):")
for cat in target_cats:
    best_grp   = avg_scores[cat].idxmax()
    best_avg   = avg_scores.loc[best_grp, cat]
    n          = response_counts.loc[best_grp]
    print(f"• {cat}: Group {best_grp} — avg = {best_avg:.2f} (n={n})")

# --- Best Overall After Adjustment ---
best_overall_grp  = avg_scores['Overall'].idxmax()
best_overall_avg  = avg_scores.loc[best_overall_grp, 'Overall']
n_overall        = response_counts.loc[best_overall_grp]
print(f"\n🥇 Best Overall Group (Adjusted): Group {best_overall_grp} — avg = {best_overall_avg:.2f} (n={n_overall})")
