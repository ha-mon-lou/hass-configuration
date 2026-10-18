# Inventario de paquetes y automatizaciones

Este documento recoge los paquetes de Home Assistant bajo `myPackages` y los automatismos manuales bajo `myAutomation`, tal como se cargan en [configuration.yaml](configuration.yaml).

## Carga principal
- `automation manual: !include_dir_merge_list myAutomation`
- `automation: !include automations.yaml`
- `homeassistant: packages: !include_dir_named myPackages`

## Paquetes HA (`myPackages`)
### calefaccion
- myPackages/calefaccion/control.yaml — Caldera - Control por demanda TRVs

### clima
- myPackages/clima/aire_acondicionado.yaml — PKG AC Sync Climate a Helper, PKG AC Sync Helper a Climate, PKG AC Ejecutar IR al cambiar demanda, PKG AC Sync Meross a Climate
- myPackages/clima/comparador_clima.yaml
- myPackages/clima/grupos_clima.yaml
- myPackages/clima/indicadores.yaml

### enchufe_meross_3
- myPackages/enchufe_meross_3/meross_switch_03.yaml
- myPackages/enchufe_meross_3/scheduler.yaml — Enchufe 03 - iniciar ciclo nocturno, Enchufe 03 - ciclo cada 5 minutos, Enchufe 03 - terminar ciclo nocturno

### energy
- myPackages/energy/energy_monitoring.yaml — Aviso: consumo elevado en enchufes, Aviso: tarifa Octopus barata activa

### escenas
- myPackages/escenas/escena_alerta.yaml
- myPackages/escenas/nocturno.yaml

### inundacion
- myPackages/inundacion/sensor_sonoff_snzb_05p.yaml

### n8n
- myPackages/n8n/clima_adaptativo.yaml — Clima Adaptativo con Predicción
- myPackages/n8n/correlaciones_confort.yaml
- myPackages/n8n/inercia_termica.yaml
- myPackages/n8n/prediccion_confort.yaml

### presencia
- myPackages/presencia/columna_led_entrada.yaml
- myPackages/presencia/esphome_rfid_pro.yaml — Guardar UID RFID, Reset RFID inactivo
- myPackages/presencia/human_presence_sensor.yaml
- myPackages/presencia/luzled_living_1.yaml — Encender luzled living_1 con presencia, Apagar luzled living_1 sin presencia
- myPackages/presencia/pkg_kts_cortesia_timer.yaml
- myPackages/presencia/presencia.yaml — [Presencia] Ramon - Actualizar ubicación habitacion 02, [Presencia] Activar si alguien llega a casa, [Presencia] Desactivar si todos se van (con FOR), [Presencia] Sincronizar al iniciar Home Assistant, ...

### salud
- myPackages/salud/body_metrics.yaml — Guardar peso Ramón, Guardar IMC Ramón, Guardar peso Pau, Guardar IMC Pau
- myPackages/salud/bodymiscale/bodymiscale_common.yaml
- myPackages/salud/bodymiscale/users/bodymiscale_pau.yaml — Guardar peso Pau, Guardar impedancia Pau, Guardar impedancia baja Pau
- myPackages/salud/bodymiscale/users/bodymiscale_ramon.yaml — Guardar peso Ramón, Guardar impedancia Ramón, Guardar impedancia baja Ramón

### trastero
- myPackages/trastero/meross_scheduled.yaml
- myPackages/trastero/meross_switch_01.yaml
- myPackages/trastero/meross_switch_01_washing_machine.yaml — Actualizar estado WashingMachine
- myPackages/trastero/meross_switch_02.yaml

### ventilacion
- myPackages/ventilacion/CO2/gestion.yaml — alertas CO2 Habitación 2, alertas CO2 Habitación 1
- myPackages/ventilacion/extractor_bathroom_1.yaml — Iniciar temporizador extractor bathroom 01 al encender, Encender extractor bathroom 01 por humedad alta, Apagar extractor bathroom 01 por humedad baja, Apagar extractor bathroom 01 tras x minutos (por temporizador), ...
- myPackages/ventilacion/ventilador_despacho.yaml — PKG VD  Ventilador Despacho - alguien regresa, PKG VD Encender ventilador despacho, PKG VD Apagar ventilador despacho, Actualizar presencia en despacho
- myPackages/ventilacion/ventilador_equation.yaml — PKG EQ Ventilador Equation - alguien regresa, PKG EQ Encender ventilador Equation desde input_boolean, PKG EQ Apagar ventilador Equation desde input_boolean, PKG EQ Oscilación ventilador Equation, ...
- myPackages/ventilacion/ventilador_habitacion.yaml — PKG VH  Ventilador habitacion - alguien regresa, PKG VH Encender ventilador habitacion, PKG VH Apagar ventilador habitacion, Actualizar presencia en habitacion
- myPackages/ventilacion/ventilador_habitacion_1.yaml
- myPackages/ventilacion/ventilador_living_1.yaml — Encender ventilador living_1 en verano con presencia, Apagar ventilador living_1 sin presencia, Sincronizar boolean con ventilador living_1
- myPackages/ventilacion/ventilador_umbrales.yaml — PKG TH Apagar ventiladores al desactivar verano

### weather
- myPackages/weather/bochorno.yaml
- myPackages/weather/forecast_alert.yaml — Reset luces alerta forecast, Reset alerta forecast, Notificación de alerta meteorológica
- myPackages/weather/forecast_scheduler.yaml — Forecast scheduler
- myPackages/weather/forecast_trip.yaml — Resumen trayecto moto al desenchufar móvil

### webhooks
- myPackages/webhooks/abrir_puerta.yaml
- myPackages/webhooks/luz_habitacion_2.yaml

### yale
- myPackages/yale/alerta.yaml — Notificar puerta abierta más de 10 minutos, Responder notificación interactiva - cerrar puerta, Registrar respuesta "sí, lo sé
- myPackages/yale/cerradura.yaml — Iniciar o reiniciar temporizador de bloqueo al cerrar puerta, Bloquear puerta al terminar temporizador

## Automatizaciones manuales (`myAutomation`)
### NFC
- myAutomation/NFC/etiqueta-despacho.yaml
- myAutomation/NFC/etiqueta-habitacion_2_puerta.yaml
- myAutomation/NFC/etiqueta-piano.yaml
- myAutomation/NFC/etiqueta-yale-exterior.yaml
- myAutomation/NFC/etiqueta-yale-interior.yaml
- myAutomation/NFC/temporizador-helper.yaml
- myAutomation/NFC/temporizador.yaml
- myAutomation/NFC/youtube.yaml

### broadLink
- myAutomation/broadLink/ventiladores/ventiladores_apagar.yaml

### calefaccion
- myAutomation/calefaccion/auto-calibracion.yaml
- myAutomation/calefaccion/boton_send_confort.yaml
- myAutomation/calefaccion/invierno.yaml
- myAutomation/calefaccion/test-calefaccion.yaml
- myAutomation/calefaccion/trigger_on_temperatura_change.yaml
- myAutomation/calefaccion/trigger_on_termostato_virtual_off.yaml
- myAutomation/calefaccion/trigger_on_trvs.yaml

### calendar
- myAutomation/calendar/calendar-DL.yaml

### iotLink
- myAutomation/iotLink/despierta.yaml

### lavavajillas
- myAutomation/lavavajillas/trigger_on_sch_lavavajillas.yaml

### luces
- myAutomation/luces/myBox.yaml
- myAutomation/luces/secuencia.yaml
- myAutomation/luces/tele-on-luces-off.yaml
- myAutomation/luces/vigilancia-luces.yaml

### mediaPlayer
- myAutomation/mediaPlayer/update-titulo-video.yaml

### pulsadores
- myAutomation/pulsadores/ikea_somrig/ikea_somrig_01.yaml
- myAutomation/pulsadores/scene_switch/moes_scene_switch_02.yaml
- myAutomation/pulsadores/scene_switch/moes_zt_b_eu2_01.yaml
- myAutomation/pulsadores/scene_switch/scene_switch_01.yaml
- myAutomation/pulsadores/shelly_button1/encender_luz_piano.yaml — Encender luz piano con botón Shelly BLU 908F
- myAutomation/pulsadores/shelly_button1/luz-entrada.yaml — Abrir puerta con botón Shelly BLU 908F, Retardo Abrir puerta con botón Shelly BLU 908F
- myAutomation/pulsadores/shelly_button_tough_01/abrir_puerta.yaml — Abrir puerta con botón Shelly BLU a16c tough
- myAutomation/pulsadores/shelly_button_tough_01/luz_entrada.yaml — Encender luz con botón Shelly BLU a16c tough
- myAutomation/pulsadores/shelly_ht_button/press-toggle-studioBricks-luz.yaml

### shutdown
- myAutomation/shutdown/secuencia-switches.yaml
- myAutomation/shutdown/secuencia.yaml

### studioBricks
- myAutomation/studioBricks/studioBricks-aire-scheduled.yaml
- myAutomation/studioBricks/studioBricks-luz.yaml

### sun
- myAutomation/sun/sun.yaml

### timer
- myAutomation/timer/custom_temporizador1.yaml
- myAutomation/timer/custom_temporizador2.yaml
- myAutomation/timer/despertador.yaml
- myAutomation/timer/temporizador_luces.yaml

### watchdog
- myAutomation/watchdog/zigbee2mqtt.yaml — WD Watchdog Zigbee Devices Offline

## Automatizaciones en raíz
- automations.yaml — BP Bring!
- myAutomation/recordatorios_espaciales.yaml — Recordatorios espaciales

