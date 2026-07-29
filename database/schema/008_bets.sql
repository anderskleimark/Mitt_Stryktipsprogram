CREATE TABLE IF NOT EXISTS bets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coupon_id INTEGER NOT NULL,
    system_id INTEGER NOT NULL,
    bet_date TEXT NOT NULL,
    correct_count INTEGER,
    prize INTEGER,
    FOREIGN KEY(coupon_id)
    REFERENCES coupons(id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
    FOREIGN KEY(system_id)
    REFERENCES systems(id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT
);
        
CREATE TABLE IF NOT EXISTS bet_details (
    bet_id INTEGER NOT NULL,
    match_number INTEGER NOT NULL,
    frame_value TEXT NOT NULL,
    key_value TEXT,
    mathematical_value INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY(bet_id, match_number),
    FOREIGN KEY(bet_id)
    REFERENCES bets(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);