DROP FUNCTION shp.stub_cdek_packages(shp_id integer);

CREATE OR REPLACE FUNCTION shp.stub_cdek_packages(arg_shp_id integer)
 RETURNS TABLE(number character varying, weight integer, length integer, width integer, height integer)
 LANGUAGE plpgsql
AS $function$
begin
    if arg_shp_id = -111 then
        return query 
        VALUES('коробка 1'::varchar, 500, 10, 20, 30);
    else
        return query 
        VALUES('коробка 1'::varchar, 700, 10, 20, 30), ('коробка 2'::varchar, 1000, 11, 22, 33);
    end if;
end;
$function$
;
