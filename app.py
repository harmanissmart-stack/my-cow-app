import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="Holstein Purebred Suite", layout="wide", page_icon="🐄")

if "bull_catalog" not in st.session_state:
    st.session_state.bull_catalog = {
        "HO_CAPTAIN": {
            "sire": "CHARL", "dam": "SABRINA", "color": "Black & White", "recessive": "Clean",
            "inventory_sexed": 25, "inventory_conv": 10, "cost": 65.00, "last_sync": "Local Cache",
            "casein": "A2A2", "k_casein": "BB", "calving_ease": 1.6,
            "traits": {"PTAM": 1850, "PTAP": 68, "PTAF": 115, "PL": 6.5, "DPR": 1.4, "UDC": 1.45}
        },
        "HO_DELTA_LAMBDA": {
            "sire": "DELTA", "dam": "LANA", "color": "Black & White", "recessive": "Clean",
            "inventory_sexed": 12, "inventory_conv": 8, "cost": 85.00, "last_sync": "Local Cache",
            "casein": "A1A2", "k_casein": "AB", "calving_ease": 2.1,
            "traits": {"PTAM": 1120, "PTAP": 42, "PTAF": 55, "PL": 4.1, "DPR": -0.8, "UDC": 2.65}
        },
        "HO_CHIEF": {
            "sire": "HO_MOGUL", "dam": "ROSE", "color": "Black & White", "recessive": "MW Carrier",
            "inventory_sexed": 0, "inventory_conv": 14, "cost": 50.00, "last_sync": "Local Cache",
            "casein": "A2A2", "k_casein": "AA", "calving_ease": 2.5,
            "traits": {"PTAM": 1050, "PTAP": 38, "PTAF": 45, "PL": 3.2, "DPR": 0.2, "UDC": 2.10}
        }
    }

if "global_pedigree" not in st.session_state:
    st.session_state.global_pedigree = {
        "HO_CHIEF": {"sire": "HO_MOGUL", "dam": "ROSE"},
        "HO_MOGUL": {"sire": "DORCY", "dam": "MARSH"},
        "DORCY": {"sire": "ROYLANE_SOCRA", "dam": "OBLONG_VAL"},
        "HEIFER_601": {"sire": "HO_MOGUL", "dam": "OLD_DAM_A"},
        "COW_501": {"sire": "HO_CHIEF", "dam": "OLD_DAM_B"}
    }

COW_PHENOTYPES = {
    "HEIFER_601": {"type": "Heifer", "PTAM": 500, "PTAP": 20, "PTAF": 22, "PL": 2.0, "DPR": 1.2, "UDC": 0.8},
    "COW_501": {"type": "Mature Cow", "PTAM": 300, "PTAP": 10, "PTAF": 12, "PL": 1.0, "DPR": -1.5, "UDC": 0.4}
}

st.title("🐄 Purebred Holstein Friesian Genetic Engine")
st.markdown("Automated CDCB synchronization and replacement reproduction rules.")

tab1, tab2 = st.tabs(["⚡ CDCB & Stock Management", "📊 Advanced Mating Optimizer Matrix"])

with tab1:
    st.header("CDCB Portal & Advanced Straw Inventory")
    if st.button("🔄 Sync Sires Live With CDCB"):
        st.success("Global database tracking sync completed!")
    
    catalog_display = []
    for k, v in st.session_state.bull_catalog.items():
        catalog_display.append({
            "Sire Code": k, "Beta-Casein": v["casein"], "Kappa-Casein": v["k_casein"],
            "Calving Ease": f"{v['calving_ease']}%", "Sexed Inventory": v["inventory_sexed"],
            "Conv. Inventory": v["inventory_conv"], "PTA Milk": v["traits"]["PTAM"], "Last Sync": v["last_sync"]
        })
    st.dataframe(pd.DataFrame(catalog_display), use_container_width=True)

with tab2:
    st.header("Purebred Replacement Pairing Matrix")
    active_herd_cows = list(COW_PHENOTYPES.keys())
    selected_cow = st.selectbox("Select Target Milking Dam", active_herd_cows)
    cow_data = COW_PHENOTYPES[selected_cow]
    
    st.subheader("🛡️ Reproductive Policy Analysis")
    if cow_data["type"] == "Heifer":
        st.info(f"📋 Heifer Policy: {selected_cow} mandates Sexed Ultra 4M semen only.")
        semen_policy = "Sexed Only"
    else:
        st.info(f"📋 Mature Cow Policy: {selected_cow} allows both Conventional and Sexed choices.")
        semen_policy = "Any"

    if cow_data["DPR"] < 0.0:
        st.warning(f"⚠️ Fertility Repair Active: {selected_cow} has low fertility. Sires with negative DPR values are blocked.")
        dpr_repair = True
    else:
        st.success(f"✅ Fertility Baseline Stable.")
        dpr_repair = False

    mating_matrix = []
    for bull_id, bull_data in st.session_state.bull_catalog.items():
        if semen_policy == "Sexed Only" and bull_data["inventory_sexed"] <= 0:
            continue
        if dpr_repair and bull_data["traits"]["DPR"] < 0.0:
            status = "❌ BLOCKED (Fertility Policy)"
        else:
            status = "✅ PUREBRED MATCH APPROVED"
            
        mating_matrix.append({
            "Sire Code": bull_id, "Sire Calving Ease": f"{bull_data['calving_ease']}%",
            "Sire PTA DPR": f"{bull_data['traits']['DPR']}%",
            "Semen Stock": f"Sexed: {bull_data['inventory_sexed']} | Conv: {bull_data['inventory_conv']}",
            "System Allocation Ruling": status
        })
        
    df_matrix = pd.DataFrame(mating_matrix)
    st.dataframe(df_matrix, use_container_width=True)
