CREATE OR REPLACE FUNCTION shp.cdek_sender_phones(shp_id integer)
RETURNS TABLE (phone varchar(255), additional varchar (255))
LANGUAGE plpgsql
AS $function$
begin
if shp_id = 111 then
    return query 
    VALUES('+79219176597'::varchar, ''::varchar), ('81371) 948-31'::varchar, NULL::varchar); 
else
    return query 
    VALUES('+79219991122'::varchar, NULL::varchar); 
end if;

end;
$function$
;
