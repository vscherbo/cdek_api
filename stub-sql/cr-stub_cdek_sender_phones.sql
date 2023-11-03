DROP FUNCTION shp.stub_cdek_sender_phones(shp_id integer);

CREATE OR REPLACE FUNCTION shp.stub_cdek_sender_phones(shp_id integer)
RETURNS TABLE ("number" varchar(255), additional varchar (255))
LANGUAGE plpgsql
AS $function$
begin
if shp_id = -111 then
    return query 
    VALUES('+79219176597'::varchar, ''::varchar), ('81371) 948-31'::varchar, ''::varchar); 
else
    return query 
    VALUES('+79219991122'::varchar, ''::varchar); -- field "additional" not NULL, but empty string
end if;

end;
$function$
;
