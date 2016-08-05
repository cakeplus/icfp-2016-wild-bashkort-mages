
open Batteries
open Num
open Utils
open Geometry


let interactive = ref false
let problem_file = ref ""
let dissect_step = num_of_int 10
let iterations = 1


let gen_dissections (sol: Solution.t) =
  let hull = sol |> List.map fst |> Geometry.convex_hull in
  let vertexes =
    collect (fun push ->
      let hull = List.tl hull in
      List.combine hull (rotate hull) |> List.iter (fun ((x1, y1), (x2, y2)) ->
         let slope_x = (x2 -/ x1) // dissect_step in
         let slope_y = (y2 -/ y1) // dissect_step in
         push (`Existing, (x1, y1));
         let x0 = ref (x1 + slope_x) in
         let y0 = ref (y1 + slope_y) in
         while !x0 <> x2 || !y0 <> y2 do
           push (`New, (!x0, !y0));
           x0 := !x0 + slope_x;
           y0 := !y0 + slope_y;
         done))
  in
  collect (fun push ->
    vertexes |> List.iter (fun (kind1, v1) ->
      vertexes |> List.iter (fun (kind2, v2) ->
        if Geometry.compare_vertex v1 v2 > 0 then
          begin
            let line = Geometry.compute_line v1 v2 in
            let sol = if kind1 = `New then (v1, v1) :: sol else sol in
            let sol = if kind2 = `New then (v2, v2) :: sol else sol in
            push (line, sol)
          end)))

let apply_dissection target ((l: line), (sol: Solution.t)) : (Solution.t * area) option =
  let hull_old = sol |> List.map fst |> Geometry.convex_hull in
  let sol' = sol |> List.map (fun (v1, v0) ->
    let v1' = Geometry.flip_vertex l v1 in
    (v1', v0))
  in
  let hull_new = sol' |> List.map fst |> Geometry.convex_hull in
  let hull_union = Geometry.convex_hull (hull_old @ hull_new) in
  if Geometry.hulls_are_equal hull_union hull_old then
    None
  else
    let hull_union = Geometry.convex_hull (hull_new @ target) in
    if Geometry.hulls_are_equal hull_union hull_new then
      None
    else
      Some (sol', Geometry.hull_area hull_new)

let apply_best_dissection target sol : Solution.t option =
  let sects = gen_dissections sol in
  let forks = sects |> List.filter_map (apply_dissection target) in
  let best = ref None in
  let min_area = ref num_1 in
  forks |> List.iter (fun (sol, area) ->
    if area < !min_area then
      (min_area := area;
       best := Some sol));
  !best

let apply_all_dissections target sol : unit =
  let sects = gen_dissections sol in
  sects |> List.iter (fun (line, sol) ->
    Printf.printf "line: a = %s, b = %s, c = %s\n"
      (string_of_num line.a)
      (string_of_num line.b)
      (string_of_num line.c);
    Drawing.draw_line line;
    match apply_dissection target (line, sol) with
      | Some (sol', area) ->
          Printf.printf "area: %s\n" (string_of_num area);
          Drawing.draw_solution target sol'
      | None ->
          ())

let () =
  Arg.parse (Arg.align
    [
      ("-interactive", Arg.Unit (fun () -> interactive := true),
       " Interactive mode");
    ])
    (fun s -> problem_file := s)
    ("Usage: " ^ Sys.argv.(0) ^ "[options]");

  let (sl, sk) = Problem.read_file ~fname:!problem_file in
  if !interactive then
    Drawing.draw_skeleton sk;
  if !interactive then
    Drawing.draw_silhouette sl;

  let target = Geometry.convex_hull (List.concat sl) in
  if !interactive then
    Drawing.draw_poly target;

  let fitted_target =
    match Geometry.fit_poly target with
      | Some t -> t
      | None ->
          failwith "Couldn't fit the target!"
  in
  if !interactive then
    Drawing.draw_poly fitted_target;

  apply_all_dissections target Solution.default;

  let sol =
    match apply_best_dissection target Solution.default with
      | Some sol ->
          sol
      | None ->
          failwith "Unable to find solution!"
  in
  if !interactive then
    Drawing.draw_solution target sol
