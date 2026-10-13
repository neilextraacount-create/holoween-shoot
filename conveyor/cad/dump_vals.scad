// Prints the derived dimensions the Python checker needs:  openscad -o x.echo dump_vals.scad
include <conveyor.scad>
part = "none";
vals = [["L_w", L_w], ["half_w", half_w], ["side_in", side_in], ["side_out", side_out], ["Y_c", Y_c], ["Y_p", Y_p],
        ["drv_rs", drv_rs], ["drv_jlen", drv_jlen], ["drv_pin_z0", drv_pin_z0], ["hz_g", hz_g], ["h_feet", h_feet],
        ["ua", ua], ["gb_top_s", gb_top_s], ["seg_len", seg_len], ["seg_count", seg_count], ["tp_u0", tp_u0],
        ["tz_g", tz_g], ["t_tabs", t_tabs], ["tu_in", tu_in], ["tu_out", tu_out], ["scr_y", scr_y], ["tb_pad", tb_pad],
        ["tn_t", tn_t], ["t_rear", t_rear], ["st_carry_z", st_carry_z], ["st_ret_z", st_ret_z], ["st_ret_top", st_ret_top],
        ["st_y0", st_y0], ["st_bot", st_bot], ["spig", spig], ["ch_len", ch_len], ["belt_w", belt_w], ["belt_t", belt_t],
        ["tail_r", tail_r], ["roll_crown", roll_crown], ["wu_r", wu_r], ["wu_crown", wu_crown], ["sq_z", sq_z], ["crank_r", crank_r],
        ["aw", aw], ["st_q", st_q], ["st_len", st_len], ["spike_sock", spike_sock], ["stand_h", stand_h], ["post_b", post_b],
        ["spike_head", spike_head], ["spig_len", spig_len], ["cb_d", cb_d], ["slv_len", slv_len], ["ca_t", ca_t],
        ["crank_head_len", crank_head_len], ["sock_len", sock_len], ["wl_top", wl_top], ["fl_bot", fl_bot], ["trough_n", trough_n],
        ["drive_r", drive_r], ["gear_face", gear_face], ["sk_anch", sk_anch], ["anchor_y", anchor_y], ["foot_t", foot_t],
        ["wu_peg0", wu_peg0], ["sock_depth", sock_depth], ["head_h", head_h], ["tail_h", tail_h], ["belt_deg", belt_deg],
        ["stake_len", stake_len], ["gs_head", gs_head], ["lug_x", lug_x], ["head_side_t", side_t], ["site_head_gap", site_head_gap], ["site_rise", site_rise], ["site_run", site_run], ["sk_hd", sk_hd], ["sk_c", sk_c], ["st_arms", st_arms], ["gb_holes", gb_holes], ["post_ub", post_ub], ["post_n", post_n], ["ph_len", ph_len], ["pu_gap", pu_gap], ["pu_spig", pu_spig], ["plain_ext", plain_ext], ["tp_top", tp_top], ["tr_in", tr_in], ["fl_top", fl_top], ["st_pin", st_pin], ["rg_len", rg_len], ["pin_d", pin_d], ["site_risers", site_risers], ["pu_dmin", pu_dmin], ["pu_dmax", pu_dmax], ["hex_af", hex_af], ["fn_z", fn_z], ["fn_w", fn_w], ["wl_top", wl_top], ["sock_tr", sock_tr], ["fn_k", fn_k], ["tr_out", tr_out], ["ch_len", ch_len], ["spike_embed", spike_embed]];
for (v = vals) echo(str("VAL ", v[0], " = ", v[1]));
