-- shp.cdek_order_status определение

-- Drop table

-- DROP TABLE shp.cdek_order_status;

CREATE TABLE shp.cdek_order_status (
    id serial4 NOT NULL,
    date_time timestamp NULL,
    order_uuid uuid NULL,
    is_return bool NULL,
    cdek_number varchar NULL,
    order_number varchar NULL,
    status_code varchar NULL,
    status_reason_code varchar NULL,
    status_date_time timestamp NULL,
    city varchar NULL,
    dt_insert timestamp NOT NULL DEFAULT clock_timestamp(),
    dt_ask timestamp NULL,
    code varchar NULL,
    is_reverse bool NULL,
    is_client_return bool NULL,
    CONSTRAINT cdek_order_status_pk PRIMARY KEY (id)
);

-- Table Triggers

create trigger accepted_ai after insert on
shp.cdek_order_status for each row
when ((new.status_code = '3'::character varying)) execute procedure fntr_cdek_chg_status();

-- Permissions

ALTER TABLE shp.cdek_order_status OWNER TO arc_energo;
GRANT ALL ON TABLE shp.cdek_order_status TO arc_energo;
