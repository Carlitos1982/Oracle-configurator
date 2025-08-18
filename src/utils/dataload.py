import csv
import io
import streamlit as st


def render_dataload_panel(item_code_key: str,
                          create_btn_key: str,
                          update_btn_key: str,
                          state_key: str = "output_data"):
    st.subheader("🧾 DataLoad")
    mode = st.radio(
        "Operation type:",
        ["Create new item", "Update existing item"],
        key=f"{item_code_key}_mode"
    )

    item_code = st.text_input("Item Code", key=item_code_key)
    data = st.session_state.get(state_key, {})

    raw_q = data.get("Quality", "")
    # Gestione robusta del campo Quality
    if isinstance(raw_q, list):
        raw_q = "\n".join(raw_q)
    elif not isinstance(raw_q, str):
        raw_q = ""

    raw_q = raw_q.strip()

    if not raw_q:
        quality_tokens = ["NA"]
    else:
        quality_tokens = []
        for line in raw_q.splitlines():
            quality_tokens.append(line)
            quality_tokens.append("\\{NUMPAD ENTER}")
        if quality_tokens and quality_tokens[-1] == "\\{NUMPAD ENTER}":
            quality_tokens.pop()

    def get_val(k, default="."):
        v = data.get(k, "").strip()
        return v if v else default

    if mode == "Create new item":
        if st.button("Generate DataLoad string", key=create_btn_key):
            if not item_code:
                st.error("❌ Please enter the item code first.")
            else:
                fields = [
                    "\\%FN",            item_code,
                    "\\%TC",            get_val("Template"),
                    "TAB",
                    "\\%D", "\\%O",
                    "TAB",
                    get_val("Description"),
                    *["TAB"]*6,
                    get_val("Identificativo"),
                    "TAB",
                    get_val("Classe ricambi"),
                    "TAB",
                    "\\%O", "\\^S", "\\%TA",
                    "TAB",
                    f"{get_val('ERP_L1')}.{get_val('ERP_L2')}",
                    "TAB", "FASCIA ITE", "TAB",
                    item_code[:1], "TAB",
                    "\\^S", "\\^{F4}", "\\%TG",
                    get_val("Catalog"),
                    *["TAB"]*4,
                    get_val("Disegno"), "TAB",
                    "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", *["TAB"]*2,
                    get_val("FPD material code"), "TAB",
                    get_val("Material"), "\\^S", "\\^S", "\\^{F4}", "\\%VA",
                    "TAB", "Quality", *["TAB"]*4,
                    *quality_tokens,
                    "\\^S", "\\^{F4}", "\\^S"
                ]

                st.success("✅ DataLoad string successfully generated. Download the CSV file below.")
                buf = io.StringIO()
                writer = csv.writer(buf, quoting=csv.QUOTE_MINIMAL)
                for tok in fields:
                    writer.writerow([tok])
                st.download_button(
                    "💾 Download CSV for Import",
                    data=buf.getvalue(),
                    file_name=f"dataload_{item_code}.csv",
                    mime="text/csv",
                )

    else:
        if st.button("Generate Update string", key=update_btn_key):
            if not item_code:
                st.error("❌ Please enter the item code first.")
            else:
                fields = [
                    "\\%VF",            item_code,
                    "\\{NUMPAD ENTER}", "TAB",
                    get_val("Description", "*?"),
                    *["TAB"]*6,
                    get_val("Identificativo"), "TAB",
                    get_val("Classe ricambi"), "TAB",
                    "\\%O", "\\^S", "\\%TA",
                    "\\%VF",            "FASCIA ITE", "\\{NUMPAD ENTER}", "TAB",
                    item_code[:1],     "\\^S",
                    "\\%VF",           "TIPO ARTICOLO", "\\{NUMPAD ENTER}", "TAB",
                    f"{get_val('ERP_L1')}.{get_val('ERP_L2')}", "\\^S", "\\^{F4}",
                    "\\%TG",           get_val("Catalog"),
                    *["TAB"]*3,        get_val("Disegno"), "TAB",
                    "\\^S", "\\^{F4}", "\\^S",
                    "\\%VA",           "TAB", "Quality", *["TAB"]*4,
                    *quality_tokens,
                    "\\^S", "\\^{F4}", "\\^S"
                ]

                st.success("✅ Update string successfully generated. Download the CSV file below.")
                buf = io.StringIO()
                writer = csv.writer(buf, quoting=csv.QUOTE_MINIMAL)
                for tok in fields:
                    writer.writerow([tok])
                st.download_button(
                    "💾 Download CSV for Update",
                    data=buf.getvalue(),
                    file_name=f"update_{item_code}.csv",
                    mime="text/csv",
                )
