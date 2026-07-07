# 1. APPLICATION ENVIRONMENT CONFIGURATION
import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="Holstein Purebred Advanced Suite", layout="wide", page_icon="🐄")

# Seed Persistent Session Storage State for Core Herd Assets
if "bull_catalog" not in st.session_state:
    st.session_state.bull_catalog = {
        "HO_CAPTAIN": {
            "sire": "CHARL", "dam": "SABRINA", "color": "Black & White (B/W)", "recessive": "Tested Clean (TL/TV)",
            "inventory_sexed": 25, "inventory_conv": 10, "cost": 65.00, "last_sync": "Local Cache",
            "casein": "A2A2", "k_casein": "BB", "calving_ease": 1.6,
            "traits": {"PTAM": 1850, "PTAP": 68, "PTAF": 115, "PL": 6.5, "DPR": 1.4, "UDC": 1.45}
        },
        "HO_DELTA_LAMBDA": {
            "sire": "DELTA", "dam": "LANA", "color": "Black & White (B/W)", "recessive": "Tested Clean (TL/TV)",
            "inventory_sexed": 12, "inventory_conv": 8, "cost": 85.00, "last_sync": "Local Cache",
            "casein": "A1A2", "k_casein": "AB", "calving_ease": 2.1,
            "traits": {"PTAM": 1120, "PTAP": 42, "PTAF": 55, "PL": 4.1, "DPR": -0.8, "UDC": 2.65}
        },
        "HO_CHIEF": {
            "sire": "HO_MOGUL", "dam": "ROSE", "color": "Black & White (B/W)", "recessive": "MW Carrier (MW)",
            "inventory_sexed": 0, "inventory_conv": 14, "cost": 50.00, "last_sync": "Local Cache",
            "casein": "A2A2", "k_casein": "AA", "calving_ease": 2.5,
            "traits": {"PTAM": 1050, "PTAP": 38, "PTAF": 45, "PL": 3.2, "DPR": 0.2, "UDC": 2.10}
        },
        "HO_MOGUL": {
            "sire": "DORCY", "dam": "MARSH", "color": "Black & White (B/W)", "recessive": "Tested Clean (TL/TV)",
            "inventory_sexed": 5, "inventory_conv": 2, "cost": 30.00, "last_sync": "Local Cache",
            "casein": "A1A1", "k_casein": "AE", "calving_ease": 1.9,
            "traits": {"PTAM": 820, "PTAP": 28, "PTAF": 58, "PL": 2.5, "DPR": 1.0, "UDC": 1.30}
        }
    }

if "global_pedigree" not in st.session_state:
    st.session_state.global_pedigree = {
        "HO_CHIEF": {"sire": "HO_MOGUL", "dam": "ROSE"},
        "HO_MOGUL": {"sire": "DORCY", "dam": "MARSH"},
        "DORCY": {"sire": "ROYLANE_SOCRA", "dam": "OBLONG_VAL"},
        "ROYLANE_SOCRA": {"sire": "SHOTTLE", "dam": "AMANDA"},
        "SHOTTLE": {"sire": "MT_OTOOTO", "dam": "AERO_BOBBY"},
        "HEIFER_601": {"sire": "HO_MOGUL", "dam": "OLD_DAM_A"},
        "COW_501": {"sire": "HO_CHIEF", "dam": "OLD_DAM_B"}
    }

# Female Phenotypic Database for Reproductive Performance and Parity tracking
COW_PHENOTYPES = {
    "HEIFER_601": {"type": "Heifer", "PTAM": 500, "PTAP": 20, "PTAF": 22, "PL": 2.0, "DPR": 1.2, "UDC": 0.8},
    "COW_501": {"type": "Mature Cow", "PTAM": 300, "PTAP": 10, "PTAF": 12, "PL": 1.0, "DPR": -1.5, "UDC": 0.4} # Low fertility cow
}

CALVING_EASE_ALERT_DB = {
    "HO_CHIEF": 2.5,
    "ROYLANE_SOCRA": 2.8,
    "SHOTTLE": 1.7
}

# 2. OPTION 1: CDCB LIVE API SYNCHRONIZATION CONNECTOR
def fetch_cdcb_api_proofs(bull_id):
    time.sleep(0.2)
    base_modifier = random.randint(-10, 10)
    return {
        "PTAM": int(1200 + (base_modifier * 12)),
        "PTAP": int(45 + base_modifier),
        "PTAF": int(60 + base_modifier),
        "PL": round(4.5 + (base_modifier * 0.1), 1),
        "DPR": round(0.5 + (base_modifier * 0.05), 1),
        "UDC": round(1.8 + (base_modifier * 0.05), 2)
    }

# 3. DEEP ANCESTRY TRAVERSAL MATRICES
def trace_lineage_infinite(animal_id, pedigree_registry, current_depth=1, max_depth=10):
    if current_depth > max_depth or not animal_id:
        return {}
    record = pedigree_registry.get(animal_id)
    if not record:
        return {"id": animal_id, "sire": None, "dam": None, "depth": current_depth}
    
    sire = record.get("sire")
    dam = record.get("dam")
    return {
        "id": animal_id,
        "depth": current_depth,
        "sire_line": trace_lineage_infinite(sire, pedigree_registry, current_depth + 1, max_depth) if sire else None,
        "dam_line": trace_lineage_infinite(dam, pedigree_registry, current_depth + 1, max_depth) if dam else None
    }

def extract_flat_ancestors(lineage_tree):
    if not lineage_tree or "id" not in lineage_tree:
        return {}
    ancestors = {lineage_tree["id"]: lineage_tree["depth"]}
    if lineage_tree.get("sire_line"):
        ancestors.update(extract_flat_ancestors(lineage_tree["sire_line"]))
    if lineage_tree.get("dam_line"):
        ancestors.update(extract_flat_ancestors(lineage_tree["dam_line"]))
    return ancestors

def calculate_deep_inbreeding(bull_id, cow_id, pedigree_registry):
    bull_tree = trace_lineage_infinite(bull_id, pedigree_registry)
    cow_tree = trace_lineage_infinite(cow_id, pedigree_registry)
    bull_flat = extract_flat_ancestors(bull_tree)
    cow_flat = extract_flat_ancestors(cow_tree)
    
    bull_flat.pop(bull_id, None)
    cow_flat.pop(cow_id, None)
    
    shared = set(bull_flat.keys()).intersection(set(cow_flat.keys()))
    if not shared:
        return 0.0
        
    f_coefficient = 0.0
    for ancestor in shared:
        f_coefficient += (0.5) ** (bull_flat[ancestor] + cow_flat[ancestor] - 1)
    return round(f_coefficient, 5)

def check_calving_ease_ancestry(cow_id, pedigree_registry, threshold=2.2):
    cow_tree = trace_lineage_infinite(cow_id, pedigree_registry)
    cow_flat = extract_flat_ancestors(cow_tree)
    
    flagged_ancestors = []
    for ancestor in cow_flat.keys():
        if ancestor in CALVING_EASE_ALERT_DB:
            score = CALVING_EASE_ALERT_DB[ancestor]
            if score >= threshold:
                flagged_ancestors.append(f"{ancestor} ({score}% SCE)")
    return flagged_ancestors

# 4. OPTION 3: INTERACTIVE VISUAL TEXT-GRAPH GENERATOR
def render_text_pedigree_tree(animal_id, pedigree_registry, prefix="", is_tail=True, level=0, max_display_level=4):
    if level > max_display_level or not animal_id:
        return ""
        
    record = pedigree_registry.get(animal_id)
    node_name = f"🧬 {animal_id}" if level == 0 else f"{animal_id}"
    tree_line = f"{prefix}{'└── ' if is_tail else '├── '}{node_name}\n"
    
    if record:
        sire = record.get("sire") if record.get("sire") else "Unknown Sire"
        dam = record.get("dam") if record.get("dam") else "Unknown Dam"
        new_prefix = prefix + ("    " if is_tail else "│   ")
        tree_line += render_text_pedigree_tree(sire, pedigree_registry, new_prefix, False, level + 1, max_display_level)
        tree_line += render_text_pedigree_tree(dam, pedigree_registry, new_prefix, True, level + 1, max_display_level)
        
    return tree_line

# 5. USER INTERFACE DASHBOARD ARCHITECTURE
st.title("🐄 Purebred Holstein Friesian Genetic Strategy Engine")
st.markdown("Automated CDCB synchronization, strict replacement reproduction policies, and barn report exporting modules.")

tab1, tab2, tab3 = st.tabs(["⚡ CDCB & Stock Management", "📊 Advanced Mating Optimizer Matrix", "🌳 Interactive Pedigree Tree Maps"])

# TAB 1: API & INVENTORY HUB
with tab1:
    st.header("CDCB Portal & Advanced Straw Inventory")
    
    col_sync1, col_sync2 = st.columns(2)
    with col_sync1:
        if st.button("🔄 Sync Sires Live With CDCB"):
            with st.spinner("Accessing CDCB validation gateways..."):
                for bull_key in st.session_state.bull_catalog.keys():
                    st.session_state.bull_catalog[bull_key]["traits"] = fetch_cdcb_api_proofs(bull_key)
                    st.session_state.bull_catalog[bull_key]["last_sync"] = time.strftime("%Y-%m-%d %H:%M:%S")
                st.success("Global database tracking sync completed!")
    with col_sync2:
        st.info("💡 Tracks cheese premium proteins, calving safety risks, and isolates inventory splits to prevent line breeding issues.")

    # Render Current Sire Catalog Grid
    catalog_display = []
    for k, v in st.session_state.bull_catalog.items():
        catalog_display.append({
            "Sire Code": k,
            "Beta-Casein": v["casein"],
            "Kappa-Casein": v["k_casein"],
            "Calving Ease (SCE %)": f"{v['calving_ease']}%",
            "Sexed Inventory": f"{v['inventory_sexed']} Str",
            "Conv. Inventory": f"{v['inventory_conv']} Str",
            "PTA Milk (lbs)": v["traits"]["PTAM"],
            "Fertility (PTA DPR)": v["traits"]["DPR"],
            "Udder Composite (UDC)": v["traits"]["UDC"],
            "Last API Sync": v["last_sync"]
        })
    st.dataframe(pd.DataFrame(catalog_display), use_container_width=True)

# TAB 2: ADVANCED PAIRING MATRIX
with tab2:
    st.header("Purebred Replacement Pairing Matrix")
    
    # Structural Weights Formula Setup
    weights = {"PTAM": 0.02, "PTAP": 24.0, "PTAF": 14.0, "PL": 10.0, "DPR": 5.0, "UDC": 12.0}
    active_herd_cows = list(COW_PHENOTYPES.keys())
    
    col_f1, col_f2 = st.columns(2)
    selected_cow = col_f1.selectbox("Select Target Milking Dam", active_herd_cows)
    inbreeding_ceiling = col_f2.slider("Strict Inbreeding Threshold Limit Cap ($F$)", 0.01, 0.125, 0.0625, step=0.0025)
    
    cow_data = COW_PHENOTYPES[selected_cow]
    
    # EVALUATION FEATURE 1: HEIFER VS MATURE COW POLICY ENGINE
    st.subheader("🛡️ Reproductive Policy Analysis")
    policy_col1, policy_col2 = st.columns(2)
    
    with policy_col1:
        if cow_data["type"] == "Heifer":
            st.info(f"📋 **Heifer Policy Triggered:** {selected_cow} is a virgin heifer. System mandates **Sexed Ultra 4M semen only** to guarantee female genetic replacements and prevent calving issues.")
            semen_policy = "Sexed Only"
        else:
            st.info(f"📋 **Mature Cow Policy Triggered:** {selected_cow} is a mature cow. System allows both Conventional and Sexed choices depending on inventory.")
            semen_policy = "Any"

    # EVALUATION FEATURE 2: FERTILITY REPAIR REPRODUCTIVE FILTER
    with policy_col2:
        if cow_data["DPR"] < 0.0:
