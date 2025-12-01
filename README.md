SELECT 
      [id],
      [fecha],
      [detalle],
      [sustento],
      [pdf],
      [codigo_pago],
      [gastos_soles],
      [gastos_dolares],
      [fecha_registro],
      [seguimiento_id],
      [editor],
      [fecha_registro2],
      [usuario_id]
FROM [SDI].[dbo].[tramites_gastotramite]
WHERE fecha > '2025-10-17';


http://127.0.0.1:8000/productivity/api/events/
http://127.0.0.1:8000/productivity/calendar/
http://127.0.0.1:8000/productivity/activity/add/
http://127.0.0.1:8000/productivity/activity/4/edit/
http://127.0.0.1:8000/productivity/activity/4/score/
http://127.0.0.1:8000/productivity/reports/user/1/

tengo un proyecto en django python pero quiero ir de frente al bug q encuentro y es que tengo una plantilla home.html que tiene filtros mediante js dentro de una tabla de expedientes donde si le das click te lleva al seguimiento del expediente dentro de los tantos seguimientos que tengo es q si actualizo todo bien se guarda pero si retrocedo no se ve los cambios reflejados ya que hay un trigger en el seguimiento  que actualiza un campo de la tabla general de expedientes

Logré solucionarlo con esto:
window.addEventListener("pageshow", function (event) {
    if (event.persisted) {
        window.location.reload();
    }
});

Pero los filtros se restablecen a cero porque parece que recarga la pagina

como soluciono este problema ; si quieres te paso todo mi js de mi home.html:



quiero crear una app en django que sea para que los usuarios puedan colocar sus actividades del dia y aquella persona con permisos admin pueda ver lo que han colocado y calificar dicha actividad del 1 al 3 que se pueda hacer como un aclendario para que al darle click a la fecha ahi coloquen o si tienes otra mejor idea hazlo

SP
```sql
CREATE OR ALTER PROCEDURE dbo.sp_get_alertas_expedientes
    @responsable INT  -- parámetro para filtrar por responsable
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        seg.fecha_alerta,
        seg.caso_id,
        cj.expediente,
        cj.responsable_id,
        CASE 
            WHEN seg.fecha_alerta <= DATEADD(DAY, 5, GETDATE()) THEN 'rojo'
            WHEN seg.fecha_alerta <= DATEADD(DAY, 15, GETDATE()) THEN 'amarillo'
            ELSE 'verde'
        END AS color_alerta
    FROM [SDI].[dbo].[control_expediente_seguimiento] AS seg
    INNER JOIN [SDI].[dbo].[control_expediente_casojudicial] AS cj
        ON seg.caso_id = cj.id
    WHERE seg.fecha_alerta IS NOT NULL
      AND seg.fecha_alerta >= GETDATE()
      AND cj.responsable_id = @responsable   -- filtramos por responsable
    ORDER BY seg.fecha_alerta ASC; -- fecha más próxima primero
END
GO
```

# Proyecto SDI

### Política de ejecución temporalmente
```sh
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

```sh
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

```sh
find . -type f \( -name "*.css" -o -name "*.html" -o -name "*.js" \) -exec sed -i 's/#9a1413/#BF0909/g' {} +
find . -type f \( -name "*.css" -o -name "*.html" -o -name "*.js" \) -exec sed -i 's/#FFF9E8/#FFF4E6/g' {} +
```

#### ADD PATH PARTIDAS
```sh
sed -E "s/(['])([^']+\.pdf)(['])/\1documentos\/partidas\/\2\3/" con_pdf.sql > con_pdf_modificado.sql
```

### Eliminar DB

```sql
ALTER DATABASE SDI_dev SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
DROP DATABASE SDI_dev;
```

### EXCEL BuscarV

Win + R -> shell:startup

```
=SI.ERROR(BUSCARV(A4,Table1[#Todo], 9, FALSO), "")
```

Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "C:\Users\Admin\Desktop\SDI\iniciar_server.bat" & Chr(34), 0
Set WshShell = Nothing

Msg 2627, Level 14, State 1, Line 1861
Violation of UNIQUE KEY constraint 'UQ**centro_c**40F9A206D69EA8F9'. Cannot insert duplicate key in object 'dbo.centro_costos_cantacallao'. The duplicate key value is (CC-019-22).

INSERT INTO [centro_costos_cantacallao] (codigo, fecha, concepto, detalle, referencia, monto1, monto2) VALUES ('CC-019-22', '2022-06-11', 'Gastos Canta Callao', 'PINTADO DEL TEJADO Y PARTE DEL TECHO, FACHADA', '', '1356.6', '');
INSERT INTO [centro_costos_cantacallao] (codigo, fecha, concepto, detalle, referencia, monto1, monto2) VALUES ('CC-019-22', '2022-02-16', 'Municipalidad de los Olivos', '1 SOLICITUD DE CERTIFICACION DE NUMERACION A-1-4', '', '44', '');

- Codigo (identificacion del documento XX-XXX-XX -> CentroCosto-Sello-Año)
- Fecha (fecha en la q se realizó el gasto)
- Detalle (descripcion del gasto)
- Referencia (codigo del gasto bancario/boleta/)
- PDF (archivo de sustento)
- Monto Soles (monto del gasto)
- Monto Dolares (monto del gasto)
- Actividad (proyecto, obra, servicio o actividad específica donde se realizó el gasto [PinturaFachada, CajaDeLuzEnel, ReparacionDeTecho])
- Tipo Gasto (Representa para qué fin contable se usó el dinero [ManoDeObra, Materiales, etc])

- Debe -> ingresa
- Haber -> sale
  Saldo = D - H
  {% if request.user.role == 3 %}#bf616a{% elif request.user.role == 2 %}#5e81ac{% else %}#3b4252{% endif %}; border: none;

---

N°: Número correlativo del registro en la tabla. Es un identificador secuencial, en este caso es el número 83.
Expediente: Código único que identifica el proceso judicial. Incluye información como el año, número de expediente, tipo de juzgado, y otras referencias internas del sistema judicial.
Sede: Ubicación geográfica o jurisdicción del juzgado que lleva el caso
Especialidad: Categoría jurídica a la que corresponde el caso dentro del sistema judicial.
Materia: Tipo específico de asunto dentro de la especialidad jurídica. En este caso aparece como ODSD, que puede ser un código interno (por ejemplo, Obligaciones Derivadas de Servicios Domiciliarios, si fuese el caso, pero depende del sistema judicial correspondiente).
Juzgado: Nombre y dirección del juzgado que tramita el expediente.
Demandante: Persona o entidad que inician la demanda judicial.
Demandado: Persona o entidad contra quienes se interpone la demanda.
AñoInicio: Año en que se inició el proceso judicial.

1ra hoja -> todos los movimientos

```SQL
SELECT TOP (1000) [id]
      ,[anio]
      ,[url]
      ,[flag]
  FROM [SDI_dev].[dbo].[hoja_requerimiento_anios];

TRUNCATE TABLE [SDI_dev].[dbo].[hoja_requerimiento_anios];

insert into dbo.hoja_requerimiento_anios VALUES ('2025', '/q1_t1', 1);
insert into dbo.hoja_requerimiento_anios VALUES ('2025', '/q2_t1', 1);
insert into dbo.hoja_requerimiento_anios VALUES ('2026', '/q1_t2', 1);
insert into dbo.hoja_requerimiento_anios VALUES ('2026', '/q2_t2', 1);
insert into dbo.hoja_requerimiento_anios VALUES ('2027', '/q1_t3', 1);
insert into dbo.hoja_requerimiento_anios VALUES ('2027', '/q2_t3', 1);
```

PC3: 192.168.18.116

```sql
UPDATE [SDI_dev].[dbo].[control_expediente_casojudicial] SET representante = 'Demandante' WHERE representante = 'demandante';
UPDATE [SDI_dev].[dbo].[control_expediente_casojudicial] SET representante = 'Demandado' WHERE representante = 'demandado';
```

### ACTUALIZAR CON LOS ULTIMOS PENDIENTES EN TABLA CASO_JUDICIAL DE LA TABLA SEGUIMIENTO (EXPEDIENTE)
```sql
UPDATE CJ
SET pendiente = S.pendiente
FROM [SDI_dev].[dbo].[control_expediente_casojudicial] CJ
OUTER APPLY (
    SELECT TOP 1 S.pendiente
    FROM [SDI_dev].[dbo].[control_expediente_seguimiento] S
    WHERE S.caso_id = CJ.id
    ORDER BY S.fecha_seguimiento DESC, S.fecha_registro DESC
) S
WHERE S.pendiente IS NOT NULL;
```

### TRIGGER DE ACTUALIZACION AUTOMATICA (EXPEDIENTE)
```sql
ALTER TRIGGER [dbo].[trg_UpdatePendiente]
ON [dbo].[control_expediente_seguimiento]
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;

    -- Recoger todos los caso_id afectados por la operación
    DECLARE @caso_ids TABLE (caso_id INT);

    INSERT INTO @caso_ids (caso_id)
    SELECT DISTINCT caso_id FROM inserted
    UNION
    SELECT DISTINCT caso_id FROM deleted;

    -- Actualizar campos 'pendiente' y 'fecha_compromiso' en la tabla de casos judiciales
    UPDATE CJ
    SET 
        pendiente = S.pendiente,
        fecha_compromiso = S.fecha_registro
    FROM [SDI_dev].[dbo].[control_expediente_casojudicial] CJ
    INNER JOIN @caso_ids C ON CJ.id = C.caso_id
    OUTER APPLY (
        SELECT TOP 1 
            pendiente,
            fecha_registro
        FROM [SDI_dev].[dbo].[control_expediente_seguimiento] S
        WHERE S.caso_id = C.caso_id
        ORDER BY fecha_seguimiento DESC, fecha_registro DESC
    ) S;
END;
```

---

### ACTUALIZAR CON LOS ULTIMOS PENDIENTES EN TABLA TRAMITES DE LA TABLA SEGUIMIENTO (TRAMITE)
```sql
UPDATE SEG
SET pendiente = S.pendiente
FROM [SDI_dev].[dbo].[tramites_tramite] SEG
OUTER APPLY (
    SELECT TOP 1 S.pendiente
    FROM [SDI_dev].[dbo].[tramites_seguimientotramite] S
    WHERE S.caso_id = SEG.id
    ORDER BY S.fecha_seguimiento DESC, S.fecha_registro DESC
) S
WHERE S.pendiente IS NOT NULL;
```

### TRIGGER DE ACTUALIZACION AUTOMATICA (TRAMITE)
```sql
CREATE TRIGGER trg_UpdatePendienteTramite
ON [SDI_dev].[dbo].[tramites_seguimientotramite]
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    -- Recoger todos los caso_id afectados por la operación
    DECLARE @caso_ids TABLE (caso_id INT);

    INSERT INTO @caso_ids (caso_id)
    SELECT DISTINCT caso_id FROM inserted
    UNION
    SELECT DISTINCT caso_id FROM deleted;

    -- Actualizar el campo pendiente en la tabla de tramites
    UPDATE SEG
    SET pendiente = S.pendiente
    FROM [SDI_dev].[dbo].[tramites_tramite] SEG
    INNER JOIN @caso_ids C ON SEG.id = C.caso_id
    OUTER APPLY (
        SELECT TOP 1 pendiente
        FROM [SDI_dev].[dbo].[tramites_seguimientotramite] S
        WHERE S.caso_id = C.caso_id
        ORDER BY fecha_seguimiento DESC, fecha_registro DESC
    ) S;
END;
```

# ELIMINAR UN TRIGGER
```sql
DROP TRIGGER <NAME>
```

# ELIMINAR REGISTROS
```sql
DELETE FROM [SDI_dev].[dbo].[control_expediente_registroactividad]
WHERE nombre LIKE '%richar%';
DELETE FROM [SDI_dev].[dbo].[control_expediente_registroactividad]
WHERE nombre LIKE '%asd%';
```

# TRIGGER CARPETA FISCAL
```sql
CREATE TRIGGER trg_UpdatePendienteLegal
ON [SDI_dev].[dbo].[control_expediente_seguimientofiscal]
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;

    -- Recoger todos los caso_id afectados por la operación
    DECLARE @caso_ids TABLE (caso_id INT);

    INSERT INTO @caso_ids (caso_id)
    SELECT DISTINCT caso_id FROM inserted
    UNION
    SELECT DISTINCT caso_id FROM deleted;

    -- Actualizar el campo pendiente en la tabla de casos judiciales
    UPDATE CJ
    SET pendiente = S.pendiente
    FROM [SDI_dev].[dbo].[control_expediente_carpetafiscal] CJ
    INNER JOIN @caso_ids C ON CJ.id = C.caso_id
    OUTER APPLY (
        SELECT TOP 1 pendiente
        FROM [SDI_dev].[dbo].[control_expediente_seguimientofiscal] S
        WHERE S.caso_id = C.caso_id
        ORDER BY fecha_seguimiento DESC, fecha_registro DESC
    ) S;
END;
```

# LISTAR TRIGGERS
```sql
SELECT 
    name AS trigger_name,
    OBJECT_NAME(parent_id) AS table_name,
    type_desc
FROM sys.triggers
WHERE parent_class_desc = 'OBJECT_OR_COLUMN';

```

### SSH
```
ssh user@192.168.18.121 : 12345
```

```
python manage.py sqlmigrate asistencia 0001_initial
```

crear el trigger cuando se actualiza la tabla principal tramites el campo actualizacion

# TRIGGER HORAS TRABAJADAS
```sql
CREATE OR ALTER TRIGGER trg_calcular_horas
ON asistencia_asistencia
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE a
    SET 
        horas_trabajadas = CASE 
            WHEN i.hora_entrada IS NOT NULL AND i.hora_salida IS NOT NULL
            THEN CAST(
                DATEADD(
                    SECOND, DATEDIFF(SECOND, i.hora_entrada, i.hora_salida) - 3600, 0
                ) AS TIME
            )
            ELSE NULL
        END,

        -- ✅ horas_trabajadas - 9 horas
        hora_resto = CASE 
            WHEN i.hora_entrada IS NOT NULL AND i.hora_salida IS NOT NULL
            THEN (DATEDIFF(SECOND, i.hora_entrada, i.hora_salida) - 3600) - (9 * 3600)
            ELSE NULL
        END
    FROM asistencia_asistencia a
    INNER JOIN inserted i ON a.id = i.id;
END;
GO
```

----------------------------------------------------

curl -X POST "https://zlink.minervaiot.com/zlink-api/v1.0/zlink/customer/sso/login" \
  -H "Content-Type: application/json" \
  -d '{
    "userName": "soporte@bienes-raices-santa-clara-sac.com",
    "password": "asd123$!A"
  }'

{"code":"CVAI0000","message":"Login successful","data":{"lastName":"SAC","token_type":"Bearer","userName":"soporte@bienes-raices-santa-clara-sac.com","userId":"0a0802c1993c19998199a0acf9633344","access_token":"eyJraWQiOiJyc2Ffa2V5X2lkIiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiI3NW
FhOTRlYWRhZTU0NTFmOTQzZTc0ZDhiOTEwZjVjMSIsImxhc3ROYW1lIjoiU0FDIiwidXNlcl9uYW1lIjoic29wb3J0ZUBiaWVuZXMtcmFpY2VzLXNhbnRhLWNsYXJhLXNhYy5jb20iLCJ1c2VySWQiOiIwYTA4MDJjMTk5M2MxOTk5ODE5OWEwYWNmOTYzMzM0NCIsImNsaWVudF9pZCI6Ijc1YWE5NGVhZGFlNTQ1MWY5NDNlNzRkOGI5MTBmNWMxIiwicGFzc3dvc
mRBZ2UiOjIxLCJhdWQiOiI3NWFhOTRlYWRhZTU0NTFmOTQzZTc0ZDhiOTEwZjVjMSIsImZpcnN0TmFtZSI6IkJSU0MiLCJsYXN0TG9naW5Db21wYW55SWQiOiIwYTA4MDJjMTk5M2MxOTk5ODE5OWEwYWUzMjdkMzM0NiIsInNjb3BlIjoiV1JJVEUiLCJleHBpcnlBdCI6IjIwMjUtMTAtMjNUMTQ6NDQ6MDYuMjUyWiIsImlzc3VlZEF0IjoiMjAyNS0xMC0yM1Qx
Mzo0NDowNi4yNTJaIiwiaWQiOiIwYTA4MDJjMTk5M2MxOTk5ODE5OWEwYWNmOTYzMzM0NCIsImV4cCI6MTc2MTIzMDY0NiwiaWF0IjoxNzYxMjI3MDQ2LCJqdGkiOiI1Yjk5M2NlZi0wZjk1LTQyMWYtODVhZi00NTNhYTRjMGU5ZGIiLCJlbWFpbCI6InNvcG9ydGVAYmllbmVzLXJhaWNlcy1zYW50YS1jbGFyYS1zYWMuY29tIn0.Z_nzHjLgtcI6dLR6wsP6vfU
1bl3ec3t17ClmvvMB5Kno9iqTnlbCJsU6XspFCAQoWxL2dEd55XYvtuSxhySIV7l4jueZ5U_m_zTj7Lq2ZG6P6luSBGbeQ49apDlz2z4w12I-DK-34967DSeR-r95cDBdtaOliBF5BWdDGT0-6g3buhoe_Vmz-nzUrMJ0pVL7mwzZDP9DaezC0zQKWRlMicR20Kkf7o8HtfrNrIrnGv15X-V6IyZknNTQlzUtG52uiXYoL9G-AEUqyessMiggPI3H10AaT2vF0egxSl
7CRLTuIoNjTvLkG2MEGCbUszIfeuyJfECHGGD05D6Csy-mnA","firstName":"BRSC","lastLoginCompanyId":"0a0802c1993c19998199a0ae327d3346","refresh_token":"eyJraWQiOiJyc2Ffa2V5X2lkIiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiI3NWFhOTRlYWRhZTU0NTFmOTQzZTc0ZDhiOTEwZjVjMSIsImxhc3ROYW1lIjoiU0FDIiwidX
Nlcl9uYW1lIjoic29wb3J0ZUBiaWVuZXMtcmFpY2VzLXNhbnRhLWNsYXJhLXNhYy5jb20iLCJ1c2VySWQiOiIwYTA4MDJjMTk5M2MxOTk5ODE5OWEwYWNmOTYzMzM0NCIsImNsaWVudF9pZCI6Ijc1YWE5NGVhZGFlNTQ1MWY5NDNlNzRkOGI5MTBmNWMxIiwicGFzc3dvcmRBZ2UiOjIxLCJhdWQiOiI3NWFhOTRlYWRhZTU0NTFmOTQzZTc0ZDhiOTEwZjVjMSIsI
mZpcnN0TmFtZSI6IkJSU0MiLCJsYXN0TG9naW5Db21wYW55SWQiOiIwYTA4MDJjMTk5M2MxOTk5ODE5OWEwYWUzMjdkMzM0NiIsInNjb3BlIjoiV1JJVEUiLCJleHBpcnlBdCI6IjIwMjUtMTEtMDZUMTM6NDQ6MDYuMjU3WiIsImlzc3VlZEF0IjoiMjAyNS0xMC0yM1QxMzo0NDowNi4yNTdaIiwiaWQiOiIwYTA4MDJjMTk5M2MxOTk5ODE5OWEwYWNmOTYzMzM0
NCIsImV4cCI6MTc2MjQzNjY0NiwiaWF0IjoxNzYxMjI3MDQ2LCJqdGkiOiI2OTY0OGJlNC1hMzYyLTRiOGItODQ2OC05N2I3ZWFmNTM0YWMiLCJlbWFpbCI6InNvcG9ydGVAYmllbmVzLXJhaWNlcy1zYW50YS1jbGFyYS1zYWMuY29tIn0.a3SAAVWRW7i6z3uuvUpqMWoZXU3ZkPrYkorVY7NODH0ogDTvJjPPKh9iHgjUal7eTyNsZHbM5lOCeD6zPOm81ZVho_v
P0q8aGbW7ijvD_nqnUhRCYu7IiScOm8PLdTg8ygmY-M08KHWD-vkdt8w7wemHi-LJsoGu0IVcJ6dbpYuR7A9TVECEdJ1XudRScuOOlEPpyfJc89GH6vBnz_xnDY74CWvT6Ui_ohKhFhH-jooYr5MQLskhSmGL4vKbted2wg89PMLw5lZYoUK9WIKf09dI5m7z_YVbJvuSXpDWq7__7VY7GdijtcQ9LDvTuyXOh-Mn8XtryoRgQCy6cusJng","expiryAt":"2025-1
0-23T14:44:06.252Z","id":"0a0802c1993c19998199a0acf9633344","issuedAt":"2025-10-23T13:44:06.252Z","expires_in":"3400","email":"soporte@bienes-raices-santa-clara-sac.com","jti":"5b993cef-0f95-421f-85af-453aa4c0e9db"}}


curl -X POST "https://zlink.minervaiot.com/api/v1.0/report_firstlast/?pageSize=20&start_date=2025-10-01&end_date=2025-10-22&pageNumber=1" -H "Content-Type: application/json" -H "Accept: application/json" -H "Authorization: Bearer eyJraWQiOiJyc2Ffa2V5X2lkIiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiI3NWFhOTRlYWRhZTU0NTFmOTQzZTc0ZDhiOTEwZjVjMSIsImxhc3ROYW1lIjoiU0FDIiwidXNlcl9uYW1lIjoic29wb3J0ZUBiaWVuZXMtcmFpY2VzLXNhbnRhLWNsYXJhLXNhYy5jb20iLCJjb21wYW55TmFtZSI6IkJpZW5lcyBSYcOtY2VzIFNhbnRhIENsYXJhIFNBQyIsImNsaWVudF9pZCI6Ijc1YWE5NGVhZGFlNTQ1MWY5NDNlNzRkOGI5MTBmNWMxIiwicGFzc3dvcmRBZ2UiOjIxLCJsYXN0TG9naW5Db21wYW55SWQiOiIwYTA4MDJjMTk5M2MxOTk5ODE5OWEwYWUzMjdkMzM0NiIsInNjb3BlIjoiUkVBRCBXUklURSIsInJvbGVDb2RlIjoiT1dORVIiLCJleHBpcnlBdCI6IjIwMjUtMTAtMjNUMTY6MDM6NTEuNzUzWiIsImlzc3VlZEF0IjoiMjAyNS0xMC0yM1QxNTowMzo1MS43NTNaIiwiaWQiOiIwYTA4MDJjMTk5M2MxOTk5ODE5OWEwYWNmOTYzMzM0NCIsImV4cCI6MTc2MTIzNTQzMSwiaWF0IjoxNzYxMjMxODMxLCJqdGkiOiI1MDcwMjVkYy1jYjU1LTRlY2UtOWVkMS1lNjFlMjFjNDhmYmEiLCJlbWFpbCI6InNvcG9ydGVAYmllbmVzLXJhaWNlcy1zYW50YS1jbGFyYS1zYWMuY29tIiwiY29tcGFueUNvZGUiOiIxRUVBMEY3QzNBQTY0NTc3OEUwOEZDMDQ3Q0NFRDlDQSIsImNvbXBhbnlUeXBlIjoiTk9ORSIsInJvbGVJZCI6IjAwMDAwMDAwN2U0ZGZmMDQwMTdlNGRmZjVjMzgwMDAzIiwidXNlcklkIjoiMGEwODAyYzE5OTNjMTk5OTgxOTlhMGFjZjk2MzMzNDQiLCJhdWQiOiI3NWFhOTRlYWRhZTU0NTFmOTQzZTc0ZDhiOTEwZjVjMSIsImZpcnN0TmFtZSI6IkJSU0MiLCJjb21wYW55SWQiOiIwYTA4MDJjMTk5M2MxOTk5ODE5OWEwYWUzMjdkMzM0NiIsInJvbGVOYW1lIjoiT3duZXIiLCJjb21wYW55VHlwZUlkIjoiOGE4NjgzYTQ4YWQxOTRkNjAxOGFkMTk0ZjZiMjAwMDkiLCJjb21wYW55VHlwZUNvZGUiOiJOT05FIn0.clcOX3kkNzFz7D1GIMUwpF4KjPTbYMDGrZ_pF6bz7ujRc7UQu-2qPY5NbEksmXxwXiw4M6qfcX00oftcaEBHgWMPHjVDH-jaE5OaleVC8EEqTf1b8rGnmfGgssuBQFH6Qg4DSQhkk_NEOtnbbhOH8AOfSs7FhVJWfCwq1QPZAg1tQ1uM32ayvxLdRs3Ozxl62Ly_D1AMbvnse1VR7wkqbZk934jUkWHKB81aoRm4HG0oldStgK0JaY2_pvEig3J3IHVdjNZVxCcuJ8UQh2CaFrWvcGjzQdyc_BGbk7EmU0lsSOwnaO1xbxaeJhRFYQ_e4a4xugpIdMwfzBmwWb_rDA" -d '{
  "start_date": "2025-10-01",
  "end_date": "2025-10-22",
  "employee_ids": ["8a8883a0995768370199a0f9d5311961"],
  "department_ids": [],
  "group_ids": [],
  "timestamp": 1761194706100
}'



Requisitos técnicos:
- Experiencia en Python (Django) y PHP (Laravel)
- Dominio de HTML, CSS y JavaScript para el desarrollo frontend
- Conocimiento en servicios de Google (Drive, Gmail, Calendar, Google Sheet) a nivel básico
- Manejo de bases de datos relacionales, preferentemente MySQL y SQL Server
- Conocimientos básicos en contenedores Docker
- Experiencia en administración de servidores Linux
- Uso de Git y GitHub para control de versiones



alt + tabulación : cambiar entre las ventanas abiertas
control + Windows + [izquierda] [derecha] : cambiar de escritorio
Windows + d : ir al escritorio
Windows + [flecha arriba] : maximizar una pestaña

control + w : cerrar una pestaña del navegador
control + tabulación : Navegar entre las pestañadel navegador
control + t : abrir nueva pestaña en el navagador
control + f5 : actualizar la pestaña actual del navegador

Windows [numero] : abrir un programa de la barra de tareas
control + shift + esc : abrir el administrador de tareas
control + s : guardar un documento 
Windows + v : historial de portapapepeles
