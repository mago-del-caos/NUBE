import streamlit.components.v1 as components

# --- CONVERSIÓN A PWA (APP DESCARGABLE) ---
def setup_pwa():
    pwa_code = """
    <script>
        // Evitar inyectar múltiples veces si la página se recarga
        if (!window.parent.document.getElementById("pwa-manifest")) {
            const head = window.parent.document.head;
            
            // 1. Vincular el manifest.json usando la CDN para evitar bloqueos de CORS
            const manifest = window.parent.document.createElement('link');
            manifest.id = "pwa-manifest";
            manifest.rel = 'manifest';
            manifest.href = "https://cdn.jsdelivr.net/gh/mago-del-caos/nube@main/manifest.json";
            head.appendChild(manifest);
            
            // 2. Icono nativo para iOS (iPhone/iPad)
            const appleIcon = window.parent.document.createElement('link');
            appleIcon.rel = 'apple-touch-icon';
            appleIcon.href = "https://cdn.jsdelivr.net/gh/mago-del-caos/nube@main/app.png";
            head.appendChild(appleIcon);
            
            // 3. Metaetiquetas para forzar la pantalla completa en móviles
            const metaApp = window.parent.document.createElement('meta');
            metaApp.name = "apple-mobile-web-app-capable";
            metaApp.content = "yes";
            head.appendChild(metaApp);
            
            const metaStatus = window.parent.document.createElement('meta');
            metaStatus.name = "apple-mobile-web-app-status-bar-style";
            metaStatus.content = "black-translucent";
            head.appendChild(metaStatus);
        }
    </script>
    """
    components.html(pwa_code, height=0)

setup_pwa()
