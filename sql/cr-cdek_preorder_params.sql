-- shp.cdek_preorder_params definition

-- Drop table

-- DROP TABLE shp.cdek_preorder_params;

CREATE TABLE shp.cdek_preorder_params (
    id serial4 NOT NULL,
    credate timestamp NULL DEFAULT now(),
    cdek_number varchar NULL,
    cdek_uuid uuid NULL,
    our_number varchar NULL,
    sts_code int4 NOT NULL DEFAULT 0, -- 0-создан, 10-принят, 20-верифицирован, 90-не принят, 91-некорректный
    ret_code int4 NULL,
    ret_msg varchar NULL,
    shp_id int4 NULL,
    payload json NULL,
    CONSTRAINT cdek_preorder_params_pk PRIMARY KEY (id)
);

-- Column comments

COMMENT ON COLUMN shp.cdek_preorder_params.sts_code IS '0-создан, 10-принят, 20-верифицирован, 90-не принят, 91-некорректный';
