> **Objetivo** · Proporcionar una referencia rápida, práctica y autocontenida para juristas, CSIRT y administradores de sistemas. Relaciona cada tipo penal con verbos rectores, ejemplos de ataque y su correspondencia con **MITRE ATT&CK**, incluyendo ahora las **Mitigaciones (M‑###)** recomendadas, más buenas prácticas de ciberhigiene.

---

## 1 · Tabla jurídica (verbos & ejemplos)

| Art. | Delito (bien jurídico) | Verbos rectores esenciales | Ejemplos de ataques / comportamientos típicos |
|------|------------------------|----------------------------|----------------------------------|
| **196 bis** | Violación de datos personales *(intimidad)* | apoderarse · acceder · copiar · modificar · retener · vender · comprar · dar tratamiento no autorizado | • *Data breach* a bases corporativas  <br> • Robo interno (*insider theft*)  <br> • *Credential‑stuffing*  <br> • Venta de listas de clientes |
| **217 bis** | Estafa informática *(patrimonio)* | manipular · influir · introducir datos falsos/incompletos en sistemas de procesamiento | • Fraude bancario on‑line con *malware*  <br> • Estafa en *e‑commerce*  <br> • *BEC* (Business Email Compromise)  <br> • *Skimming* + manipulación de transacciones |
| **229 bis** | Daño informático *(integridad de datos)* | suprimir · destruir · modificar información ajena | • *Wiper‑malware*  <br> • *Ransomware* con eliminación definitiva  <br> • *SQL/NoSQL injection* destructivo |
| **229 ter** | Sabotaje informático *(disponibilidad)* | destruir · alterar · entorpecer · impedir · obstaculizar el funcionamiento | • Ataque *DDoS* masivo  <br> • *Logic bomb* en infraestructura crítica  <br> • Borrado de *firmware* |
| **230** | Suplantación de identidad on‑line *(honra/identidad)* | suplantar identidad | • *Account‑takeover* en RRSS  <br> • *Deepfakes* para apertura de cuentas  <br> • *SIM‑swapping* |
| **231** | Espionaje informático *(secretos industriales)* | copiar · utilizar · destruir · bloquear · reciclar información confidencial | • APT corporativa que exfiltra planos  <br> • *Keylogger* en I+D  <br> • *Shadow IT* para extraer reportes |
| **232** | Instalación / propagación de *malware* | instalar · inducir a instalar · distribuir · ofrecer servicios de ataque | • Operar *botnets*  <br> • *Drive‑by download*  <br> • *USB drop attack*  <br> • *Supply‑chain attack* |
| **233** | Suplantación de páginas *(phishing)* | suplantar sitios electrónicos para obtener datos | • *Phishing* bancario (sitio clonado)  <br> • *Typosquatting*  <br> • *Homograph attack* |
| **234** | Facilitación del delito informático | facilitar · proveer · suministrar medios | • Venta de *exploit‑kits*  <br> • *Bullet‑proof hosting*  <br> • Mercado de credenciales RDP  <br> • Servicios “*DDoS‑for‑hire*” |
| **236** | Difusión de info. falsa que compromete el sistema financiero | difundir noticias o hechos falsos | • *Fake‑news* sobre quiebra bancaria  <br> • *Pump‑and‑dump* coordinado  <br> • Rumor malicioso sobre bolsa |

---

## 2 · Mapeo a MITRE ATT&CK + mitigaciones y recomendaciones

| Art. | Categoría técnica | ATT&CK<sup>†</sup> · Táctica → Técnica(s) clave | **Mitigaciones (M‑###)** | Recomendaciones generales |
|------|------------------|---------------------------------------------|----------------------------|----------------------------|
| **196 bis** | **Data Breach / Privacy** | Credential Access → **T1110** (Brute Force) · Collection → **T1213** (Data from Repositories) · Exfiltration → **T1567** (Exfiltration over Web Services) | **M1032** (Multi‑Factor Auth) · **M1041** (Encrypt Network Traffic) · **M1053** (Data Backup) | • MFA y políticas de contraseña fuertes  <br> • Cifrado en reposo/transito  <br> • DLP y registro de auditoría  <br> • Revisión periódica de accesos |
| **217 bis** | **Fraude / Manipulación de datos** | Initial Access → **T1566** (Phishing) · Impact → **T1565** (Data Manipulation) | **M1036** (Account Use Policies) · **M1017** (User Training) · **M1054** (Software Configuration) | • Gateways anti‑phishing + DMARC  <br> • Monitoreo de transacciones y alertas  <br> • Separación de funciones críticas  <br> • Control de integridad de BD |
| **229 bis** | **Data Destruction / Ransomware** | Impact → **T1485** (Data Destruction) · Impact → **T1490** (Ransomware) | **M1053** (Data Backup) · **M1048** (Disable or Remove Malware) · **M1046** (Segment Network) | • Backups inmutables y pruebas de restauración  <br> • EDR con bloqueo de procesos sospechosos  <br> • Segmentación de red  <br> • Parches y principio de mínimo privilegio |
| **229 ter** | **Denegación de Servicio / Sabotaje** | Impact → **T1498** (Network DoS) · **T1499** (Endpoint DoS) | **M1030** (Network Traffic Filtering) · **M1046** (Segment Network) | • Servicios anti‑DDoS / CDN  <br> • Rate‑limiting y WAF  <br> • Redundancia y balanceo de carga  <br> • Monitoreo de disponibilidad |
| **230** | **Identity Hijacking** | Credential Access → **T1606** (Forge Web Credentials) · Initial Access → **T1110** (Brute Force) | **M1032** (Multi‑Factor Auth) · **M1036** (Account Use Policies) | • MFA y verificación por hardware‑token  <br> • Protección contra *SIM‑swap* (límites y alertas)  <br> • Políticas de recuperación robustas  <br> • Supervisión de cambios de credenciales |
| **231** | **Corporate Espionage** | Collection → **T1056.001** (Keylogging) · Exfiltration → **T1041** (Exfiltration over C2) | **M1041** (Encrypt Network Traffic) · **M1038** (Restrict Execution) · **M1047** (Audit) | • DLP y clasificación de información  <br> • Monitor de endpoints en I+D  <br> • Control de dispositivos removibles  <br> • Threat Hunting proactivo |
| **232** | **Malware Deployment / Persistence** | Execution → **T1059** (Cmd & Script Interpreter) · Persistence → **T1547** (Boot/Logon Autostart) · Priv. Esc. → **T1055** (Process Injection) | **M1049** (Endpoint Protection) · **M1042** (Disable or Remove Feature/Program) · **M1038** (Restrict Execution) | • Whitelisting de aplicaciones  <br> • Gestión de parches  <br> • EDR/NGAV  <br> • Concientización del usuario |
| **233** | **Phishing / Site Spoofing** | Initial Access → **T1566.002** (Spearphishing Link) · Credential Access → **T1189** (Drive‑by Compromise) | **M1017** (User Training) · **M1030** (Network Traffic Filtering) · **M1032** (Multi‑Factor Auth) | • Puertas de correo y navegación segura  <br> • DNSSEC y verificación de dominios  <br> • Capacitación anti‑phishing  <br> • Aislamiento del navegador |
| **234** | **Tool Facilitation / Infrastructure** | Resource Development → **T1583** (Acquire Infrastructure) · **T1588** (Obtain Capabilities) | **M1030** (Network Traffic Filtering) · **M1047** (Audit) · **M1039** (Analyze Public Exposure) | • Inteligencia de amenazas (OSINT)  <br> • Evaluaciones de proveedores  <br> • Monitoreo de Dark Web  <br> • Políticas de reporte de vulnerabilidades |
| **236** | **Misinformation & Market Manipulation** | **ATT&CK for Influence** → I0028 (Amplification) · I0011 (Narrative Denial) | **M1070** (Monitor & Moderate Content) · **M1059** (Strategic Communication) | • Plan de comunicación de crisis  <br> • Monitoreo de medios y redes  <br> • Alianzas con CERT financiero  <br> • Educación a usuarios sobre fuentes confiables |

<sup>†</sup> Basado en **MITRE ATT&CK® v14** (Enterprise) y **ATT&CK for Influence** v1 para el art. 236.

---

### 3 · Workflow sugerido
1. **Recolecte evidencia técnica** (logs, forense, testimonios).  
2. **Seleccione la conducta principal** y ubíquela en la tabla jurídica (sección 1).  
3. **Consulte el mapeo ATT&CK** (sección 2) para entender la fase de la kill‑chain y controles asociados.  
4. **Aplique las recomendaciones** pertinentes para contener, erradicar y prevenir.  
5. **Documente agravantes** (autor interno, sistemas críticos, art. 235) y analice concurso de delitos.  
6. **Documente evidencias y cadena de custodia** conforme a las buenas prácticas de respuesta a incidentes ([plantilla ICS‑CERT](https://www.enisa.europa.eu/publications/good-practice-guide-for-certs-in-the-area-of-industrial-control-systems) / modelo ENISA); preserve hashes, firmas y la línea de tiempo de cada artefacto.

---

### Licencia y atribución
Contenido recopilado y resumido por Arkthos. Basado en legislación costarricense y standares internacionales ([Código Penal de Costa Rica](http://www.pgrweb.go.cr/scij/Busqueda/Normativa/Normas/nrm_texto_completo.aspx?nValor1=1&nValor2=5027)) y el repositorio oficial de [MITRE ATT&CK](https://attack.mitre.org/).

> _Última actualización: 19 jun 2025_

