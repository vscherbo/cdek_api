-- DROP FUNCTION shp.fntr_cdek_accepted();

CREATE OR REPLACE FUNCTION shp.fntr_cdek_accepted()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
begin
if new.code = "RECEIVED_AT_SHIPMENT_WAREHOUSE" then 
    with orig_shp as (select shp_id from cdek_preorder_params cpp where NEW.order_uuid = cdek_uuid)
       update shp.shipments
       set carr_doc = NEW.cdek_number, carr_docdt = NEW.dt_insert --или NEW.date_time + 3!!!
       where shp_id = (select shp_id from orig_shp);
end if;
end;
$function$
;

-- Permissions

ALTER FUNCTION shp.fntr_cdek_accepted() OWNER TO arc_energo;
