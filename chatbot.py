# ------------------------------------------
# MODULO 3: AI PHOTO EDITOR (AGENTIC WORKFLOW)
# ------------------------------------------
elif "Editor" in modulo_attivo:
    st.subheader("📸 Laboratorio Modifica Immagini (Agentic AI)")
    
    file_modifica = st.file_uploader("Carica l'immagine", type=["jpg", "png", "jpeg"], key="editor_img")
    
    if file_modifica:
        immagine_originale = Image.open(file_modifica).convert("RGB")
        st.image(immagine_originale, width=300)
        
        istruzione_editing = st.text_input("Istruzione:", "Falla in bianco e nero e aumenta contrasto")
        
        if st.button("Esegui Modifica"):
            with st.spinner("Elaborazione in corso..."):
                sys_prompt_editor = """Sei un AI che restituisce SOLO un JSON con questi parametri: 
                {"grayscale": bool, "blur": bool, "invert": bool, "contour": bool, "brightness": float, "contrast": float}"""
                
                risposta_ai = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": sys_prompt_editor}, {"role": "user", "content": istruzione_editing}],
                    temperature=0.0
                ).choices[0].message.content
                
                # RIMOZIONE PULITA DEI MARKDOWN
                clean_json = risposta_ai.replace("```json", "").replace("```", "").strip()
                
                try:
                    parametri = json.loads(clean_json)
                    img_editata = immagine_originale.copy()
                    
                    if parametri.get("grayscale"): img_editata = ImageOps.grayscale(img_editata).convert("RGB")
                    if parametri.get("invert"): img_editata = ImageOps.invert(img_editata)
                    if parametri.get("blur"): img_editata = img_editata.filter(ImageFilter.BLUR)
                    if parametri.get("contour"): img_editata = img_editata.filter(ImageFilter.CONTOUR)
                    
                    img_editata = ImageEnhance.Brightness(img_editata).enhance(parametri.get("brightness", 1.0))
                    img_editata = ImageEnhance.Contrast(img_editata).enhance(parametri.get("contrast", 1.0))
                    
                    st.image(img_editata, caption="Risultato")
                    buf = io.BytesIO()
                    img_editata.save(buf, format="JPEG")
                    st.download_button("📥 Scarica", data=buf.getvalue(), file_name="edit.jpg", mime="image/jpeg")
                except Exception as e:
                    st.error(f"Errore parsing JSON: {e}")
