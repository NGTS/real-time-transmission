create table transmission_sources (aperture_radius float not null, inc_prescan tinyint default 1, ref_image_id bigint not null, flux_adu float not null, y_coordinate float not null, x_coordinate float not null, id integer primary key auto_increment);
