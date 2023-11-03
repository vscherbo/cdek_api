DROP FUNCTION shp.stub_cdek_package_items_virt(shp_id integer, integer);

CREATE OR REPLACE FUNCTION shp.stub_cdek_package_items_virt(shp_id integer, box_number integer)
RETURNS TABLE (
    "name" varchar(255),
    ware_key varchar (20),
    cost numeric,
    weight integer,
    amount integer
)
LANGUAGE plpgsql
AS $function$
begin
    return query 
    VALUES
    ('Приборы'::varchar, --name
        123456789::varchar, -- fake KC
        1234.0, -- cost of box_number
        200, -- weight of box_number
        1 -- amount - fake, always 1
    );

end;
$function$
;
