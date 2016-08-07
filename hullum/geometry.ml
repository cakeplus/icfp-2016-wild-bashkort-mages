
open Batteries
open Num
open Utils


type vertex = num * num

type segment = vertex * vertex

type vector = num * num

type polygon = vertex list

type line = { a: num; b: num; c: num }

type area = num

type orientation = Zero | Positive | Negative

type pythagorean = { sin: num; cos: num }

type fit_offset = { shift: vector; angle: pythagorean }

type triangle = vertex * vertex * vertex


let compare_vertex (x1, y1) (x2, y2) =
  match compare_num x1 x2 with
    | 0 ->
        compare_num y1 y2
    | etc ->
        etc

let equal_vertices v1 v2 =
  compare_vertex v1 v2 = 0

let print_vertex (x, y) =
  Printf.sprintf "%s,%s" (string_of_num x) (string_of_num y)

let triple_orientation (ox, oy) (ax, ay) (bx, by) : [ `CW | `CCW | `COLL ] =
  let res = compare_num ((ax - ox)*(by - oy)) ((ay - oy)*(bx - ox)) in
  if res = 0 then
    `COLL
  else if res < 0 then
    `CW
  else
    `CCW

(* Алгоритм Андрея :) *)
let convex_hull points : polygon =

  let build_arc l =
    l |> ListLabels.fold_right ~init:[] ~f:(fun x acc ->
      let rec filter acc' =
        match acc' with
          | a :: (b :: _ as rest) when triple_orientation b a x <> `CCW ->
              filter rest
          | _ ->
              acc'
      in
      x :: filter acc)
  in

  let sorted = List.sort compare_vertex points in
  let rsorted = List.rev sorted in
  let lower = build_arc sorted in
  let upper = build_arc rsorted in
  let drop_first l = match l with [] -> [] | h :: t -> t in
  let h = ((List.rev (drop_first lower)) @ (List.rev upper)) in
  match h with
    | [] -> []
    | [ v ] -> h
    | v :: vs -> vs

let vector_of_ints (x, y) : vector =
  (num_of_int x, num_of_int y)

(* Precomputed table of exact pythagorean sines and cosines *)
let pythagoreans =
  [
    ("1", "0");
    ("0", "1");
    ("3/5", "4/5");
    ("5/13", "12/13");
    ("7/25", "24/25");
    ("8/17", "15/17");
    ("9/41", "40/41");
    ("11/61", "60/61");
    ("12/37", "35/37");
    ("13/85", "84/85");
    ("15/113", "112/113");
    ("16/65", "63/65");
    ("17/145", "144/145");
    ("19/181", "180/181");
    ("20/29", "21/29");
    ("20/101", "99/101");
    ("21/221", "220/221");
    ("23/265", "264/265");
    ("24/145", "143/145");
    ("25/313", "312/313");
    ("27/365", "364/365");
    ("28/53", "45/53");
    ("28/197", "195/197");
    ("29/421", "420/421");
    ("31/481", "480/481");
    ("32/257", "255/257");
    ("33/65", "56/65");
    ("33/545", "544/545");
    ("35/613", "612/613");
    ("36/85", "77/85");
    ("36/325", "323/325");
    ("37/685", "684/685");
    ("39/89", "80/89");
    ("39/761", "760/761");
    ("40/401", "399/401");
    ("41/841", "840/841");
    ("43/925", "924/925");
    ("44/125", "117/125");
    ("44/485", "483/485");
    ("48/73", "55/73");
    ("48/577", "575/577");
    ("51/149", "140/149");
    ("52/173", "165/173");
    ("52/677", "675/677");
    ("56/785", "783/785");
    ("57/185", "176/185");
    ("60/109", "91/109");
    ("60/229", "221/229");
    ("60/901", "899/901");
    ("65/97", "72/97");
    ("68/293", "285/293");
    ("69/269", "260/269");
    ("75/317", "308/317");
    ("76/365", "357/365");
    ("84/205", "187/205");
    ("84/445", "437/445");
    ("85/157", "132/157");
    ("87/425", "416/425");
    ("88/137", "105/137");
    ("92/533", "525/533");
    ("93/485", "476/485");
    ("95/193", "168/193");
    ("96/265", "247/265");
    ("100/629", "621/629");
    ("104/185", "153/185");
    ("105/233", "208/233");
    ("105/617", "608/617");
    ("108/733", "725/733");
    ("111/689", "680/689");
    ("115/277", "252/277");
    ("116/845", "837/845");
    ("119/169", "120/169");
    ("120/241", "209/241");
    ("120/409", "391/409");
    ("123/845", "836/845");
    ("124/965", "957/965");
    ("129/929", "920/929");
    ("132/493", "475/493");
    ("133/205", "156/205");
    ("135/377", "352/377");
    ("136/305", "273/305");
    ("140/221", "171/221");
    ("145/433", "408/433");
    ("152/377", "345/377");
    ("155/493", "468/493");
    ("156/685", "667/685");
    ("160/281", "231/281");
    ("161/289", "240/289");
    ("165/557", "532/557");
    ("168/457", "425/457");
    ("168/793", "775/793");
    ("175/337", "288/337");
    ("180/349", "299/349");
    ("184/545", "513/545");
    ("185/697", "672/697");
    ("189/389", "340/389");
    ("195/773", "748/773");
    ("200/641", "609/641");
    ("203/445", "396/445");
    ("204/325", "253/325");
    ("205/853", "828/853");
    ("207/305", "224/305");
    ("215/937", "912/937");
    ("216/745", "713/745");
    ("217/505", "456/505");
    ("220/509", "459/509");
    ("225/353", "272/353");
    ("228/397", "325/397");
    ("231/569", "520/569");
    ("232/857", "825/857");
    ("240/601", "551/601");
    ("248/977", "945/977");
    ("252/373", "275/373");
    ("259/709", "660/709");
    ("260/701", "651/701");
    ("261/461", "380/461");
    ("273/785", "736/785");
    ("276/565", "493/565");
    ("279/521", "440/521");
    ("280/449", "351/449");
    ("280/809", "759/809");
    ("287/865", "816/865");
    ("297/425", "304/425");
    ("300/661", "589/661");
    ("301/949", "900/949");
    ("308/533", "435/533");
    ("315/653", "572/653");
    ("319/481", "360/481");
    ("333/725", "644/725");
    ("336/505", "377/505");
    ("336/625", "527/625");
    ("341/541", "420/541");
    ("348/877", "805/877");
    ("364/725", "627/725");
    ("368/593", "465/593");
    ("369/881", "800/881");
    ("372/997", "925/997");
    ("385/673", "552/673");
    ("387/965", "884/965");
    ("396/565", "403/565");
    ("400/689", "561/689");
    ("407/745", "624/745");
    ("420/949", "851/949");
    ("429/629", "460/629");
    ("429/821", "700/821");
    ("432/793", "665/793");
    ("451/901", "780/901");
    ("455/697", "528/697");
    ("464/905", "777/905");
    ("468/757", "595/757");
    ("473/985", "864/985");
    ("481/769", "600/769");
    ("504/865", "703/865");
    ("533/925", "756/925");
    ("540/829", "629/829");
    ("555/797", "572/797");
    ("580/941", "741/941");
    ("615/953", "728/953");
    ("616/905", "663/905");
    ("696/985", "697/985");
  ]

let for_each_angle action : unit =
  pythagoreans
  |> List.sort (fun (sin1, cos1) (sin2, cos2) ->
      let open Pervasives in
      compare
        (String.length sin1 + String.length cos1)
        (String.length sin2 + String.length cos2))
  |> List.iter (fun (sin, cos) ->
      let sin = num_of_string sin in
      let cos = num_of_string cos in
      action { sin; cos };
      action { sin; cos = minus_num cos };
      action { sin = minus_num sin; cos };
      action { sin = minus_num sin; cos = minus_num cos })

let apply_vertex_angle (angle: pythagorean) ((x, y): vertex) =
  let x' = angle.cos * x - angle.sin * y in
  let y' = angle.sin * x + angle.cos * y in
  (x', y')

let apply_poly_angle (angle: pythagorean) (p: polygon) =
  p |> List.map (apply_vertex_angle angle)

let apply_vertex_shift ((shift_x, shift_y): vector) ((x, y): vertex) =
  (x + shift_x, y + shift_y)

let apply_poly_shift (shift: vector) (p: polygon) =
  p |> List.map (apply_vertex_shift shift)

let vertex_fits (x, y) : bool =
  x >=/ num_0 && x <=/ num_1 && y >=/ num_0 && y <=/ num_1

let poly_fits p : bool =
  p |> List.for_all vertex_fits

let gen_poly_shift p : vector =
  let min_x = p |> List.map fst |> List.reduce min_num in
  let min_y = p |> List.map snd |> List.reduce min_num in
  (minus_num min_x, minus_num min_y)

let fit_poly p : (polygon * fit_offset) option =
  Return.label (fun l ->
    for_each_angle (fun (angle: pythagorean) ->
      let p = apply_poly_angle angle p in
      let shift = gen_poly_shift p in
      let p = apply_poly_shift shift p in
      if poly_fits p then
        Return.return l (Some (p, { shift; angle })));
    None)

let negate_offset (off: fit_offset) : fit_offset =
  let (shift_x, shift_y) = off.shift in
  let shift = (minus_num shift_x, minus_num shift_y) in
  let angle = { off.angle with sin = minus_num off.angle.sin } in
  { shift; angle }

let apply_vertex_offset (off: fit_offset) (v: vertex) : vertex =
  v |> apply_vertex_shift off.shift |> apply_vertex_angle off.angle

let flip_vertex (l: line) ((x, y): vertex) : vertex =
  let d = l.a*x + l.b*y + l.c in
  let ab2 = l.a*l.a + l.b*l.b in
  let x' = x + num_neg2*((l.a*d)/ab2) in
  let y' = y + num_neg2*((l.b*d)/ab2) in
  (x', y')

let flip_poly (l: line) p =
  p |> List.map (flip_vertex l)

let get_line_y_by_x (l: line) x =
  (minus_num (l.a*x) - l.c) / l.b

let compute_line ((x1, y1): vertex) ((x2, y2): vertex) : line =
  let a = y2 - y1 in
  let b = x1 - x2 in
  let c = minus_num (a*x1) - b*y1 in
  { a; b; c }

let cross ((ax, ay): vector) ((bx, by): vector) : num =
  ax*by - ay*bx

let vec ((ax, ay): vertex) ((bx, by): vertex) =
  (bx - ax, by - ay)

let poly_edges (p: polygon) : segment list =
  let rotate list =
    match list with
      | [] ->
          []
      | x :: xs ->
          xs @ [ x ]
  in
  List.combine p (rotate p)

let poly_area (p: polygon) : area =
  let sum = ref num_0 in
  poly_edges p |> List.iter (fun (v1, v2) ->
    sum := !sum + cross v1 v2);
  num_1_by_2 * !sum

let absolute_poly_area (h: polygon) : area =
  abs_num (poly_area h)

let hulls_are_equal (p1: polygon) (p2: polygon) : bool =
  let rec iter = function
    | ([], []) ->
        true
    | (_, []) | ([], _) ->
        false
    | (v1 :: v1s, v2 :: v2s) ->
        if equal_vertices v1 v2 then iter (v1s, v2s) else false
  in
  iter (p1, p2)

let line_vertex_orientation (l: line) ((x, y): vertex) : orientation =
  let res = compare_num (l.a*x + l.b*y + l.c) num_0 in
  if res < 0 then
    Negative
  else if res > 0 then
    Positive
  else
    Zero

let segment_intersection (s1: segment) (s2: segment) : vertex option =
  let (a, b) = s1 and (c, d) = s2 in
  let (ax, ay) = a and (bx, by) = b and (cx, cy) = c and (dx, dy) = d in
  let lines_intersect =
    (gt_num (cross (vec c b) (vec c d) *
             cross (vec c d) (vec c a)) num_0) &&
    (gt_num (cross (vec a c) (vec a b) *
             cross (vec a b) (vec a d)) num_0)
  in
  if not lines_intersect then
    None
  else
    let dt = (bx - ax)*(cy - dy) - (cx - dx)*(by - ay) in
    let t = (num_1 / dt) * ((cx - ax)*(cy - dy) - (cx - dx)*(cy - ay)) in
    let x = ax + (bx - ax)*t in
    let y = ay + (by - ay)*t in
    Some (x, y)

let triangulate_hull (h: polygon) : triangle list =
  collect (fun push ->
    match h with
      | v1 :: rest ->
          let rec iter = function
            | v2 :: ((v3 :: _) as rest) ->
                push (v1, v2, v3);
                iter rest
            | _ -> ()
          in
          iter rest
      | _ -> ())

let triangle_is_negative ((a, b, c): triangle) : bool =
  let (x1, y1) = a and (x2, y2) = b and (x3, y3) = c in
  lt_num ((x1 - x3)*(y2 - y3)) ((x2 - x3)*(y1 - y3))

let point_on_segment ((ox, oy) as o) ((ax, ay) as a) ((bx, by) as b) =
  if (ox </ ax && ox </ bx) || (ox >/ ax && ox >/ bx) ||
     (oy </ ay && oy </ by) || (oy >/ ay && oy >/ by) then
    false
  else
    cross (vec o a) (vec o b) =/ num_0

let point_in_triangle ((a, b, c): triangle) (v: vertex) : bool =
  if point_on_segment v a b ||
     point_on_segment v b c ||
     point_on_segment v a c then
    true
  else
    let b1 = triangle_is_negative (v, a, b) in
    let b2 = triangle_is_negative (v, b, c) in
    let b3 = triangle_is_negative (v, c, a) in
    (b1 = b2) && (b2 = b3)

let get_hull_inter_points (h1: polygon) (h2: polygon) : vertex list =
  collect (fun push ->
    poly_edges h1 |> List.iter (fun seg1 ->
      poly_edges h2 |> List.iter (fun seg2 ->
        segment_intersection seg1 seg2 |> Option.may push)))

let intersect_hulls h1 h2 : polygon option =
  let inter_points = get_hull_inter_points h1 h2 in
  let set1 = triangulate_hull h1 in
  let set2 = triangulate_hull h2 in
  let h3 = h1 @ h2 @ inter_points |> List.filter (fun v ->
    set1 |> List.exists (fun t -> point_in_triangle t v) &&
    set2 |> List.exists (fun t -> point_in_triangle t v))
  in
  let h3 = convex_hull h3 in
  if absolute_poly_area h3 =/ num_0 then
    None
  else
    Some h3

let gen_huge_segment (l: line) : segment =
  if l.a =/ num_0 then
    let y0 = (minus_num l.c) / l.b in
    ((num_neg2, y0), (num_2, y0))
  else if l.b =/ num_0 then
    let x0 = (minus_num l.c) / l.a in
    ((x0, num_neg2), (x0, num_2))
  else
    ((num_neg2, get_line_y_by_x l num_neg2),
     (num_2, get_line_y_by_x l num_2))

let point_on_line ((x, y): vertex) (l: line) : bool =
  l.a*x + l.b*y + l.c =/ num_0

let line_hull_intersection (l: line) (h: polygon) =
  let seg1 = gen_huge_segment l in
  collect (fun push ->
    poly_edges h |> List.iter (fun ((v3, v4) as seg2) ->
      if point_on_line v3 l then
        push (`Existing v3)
      else
        segment_intersection seg1 seg2 |> Option.may (fun v ->
          push (`New v))))

let segments_equal ((v1, v2): segment) ((v3, v4): segment) : bool =
  (equal_vertices v1 v3 && equal_vertices v2 v4) ||
  (equal_vertices v1 v4 && equal_vertices v2 v3)

let is_poly_edge (p: polygon) (s: segment) : bool =
  Return.label (fun l ->
    poly_edges p |> List.iter (fun s' ->
      if segments_equal s s' then
        Return.return l true);
    false)
