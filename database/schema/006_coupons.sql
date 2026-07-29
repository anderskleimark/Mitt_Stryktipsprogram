CREATE TABLE IF NOT EXISTS coupons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coupon_year INTEGER NOT NULL,
    coupon_week INTEGER NOT NULL,
    UNIQUE(coupon_year, coupon_week)
);
       
CREATE TABLE IF NOT EXISTS coupon_matches (
    coupon_id INTEGER NOT NULL,
    match_number INTEGER NOT NULL,
    match_id INTEGER NOT NULL,
    PRIMARY KEY(coupon_id, match_number),
    FOREIGN KEY(coupon_id)
    REFERENCES coupons(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
    FOREIGN KEY(match_id)
    REFERENCES matches(id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
    UNIQUE(coupon_id, match_id)
);