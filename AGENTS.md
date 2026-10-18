# AGENTS.md

## Importante

Los directorios `_doc` y `_sandbox` son de respaldo, pruebas, documentación histórica y archivos de experimentación.

No forman parte de la configuración funcional activa de Home Assistant ni de la ejecución normal del sistema.

## Regla

- `_doc/`: contenido de documentación, notas, referencias, ejemplos y archivos auxiliares.
- `_sandbox/`: prototipos, pruebas, YAML experimentales y configuraciones no activas.
- Cualquier cambio en estos directorios debe considerarse como no productivo para la configuración en ejecución.

## Uso recomendado

- Usar `myPackages`, `myAutomation`, `myScripts`, `myTemplate`, `myInput`, etc. como fuentes de configuración activa.
- Tratar `_doc` y `_sandbox` como backup, histórico o laboratorio.
- No asumir que un archivo en `_doc` o `_sandbox` esté cargado por Home Assistant ni sea funcional.

## Verificación

Si una configuración no aparece en los directorios activos del sistema principal, no debe considerarse operativa salvo que se integre explícitamente en la configuración principal.

## Convención de "guarda"

Cuando el usuario diga "guarda", se debe documentar el cambio en `documentacion/openspecs/` y actualizar este `AGENTS.md`, crear un commit y hacer push. Incluir solo los archivos relacionados con el cambio; no incorporar otros cambios pendientes del usuario.
