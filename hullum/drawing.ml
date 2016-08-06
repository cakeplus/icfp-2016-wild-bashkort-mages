
open Geometry
open Graphics
open Utils


let wait () =
  let continue = ref false in
  while not !continue do
    if key_pressed () then
      if read_key () = 'q' then
        continue := true
  done

let width = 800
let height = 800

let conv_vertex ((x, y): vertex) : (int * int) =
  (truncate (Num.float_of_num x *. (float_of_int width)),
   truncate (Num.float_of_num y *. (float_of_int height)))

let with_canvas action =
  open_graph (Printf.sprintf " %dx%d" width height);
  set_color black;
  fill_rect 0 0 width height;
  action ();
  wait ()

let draw_skeleton sk =
  with_canvas (fun () ->
    set_color white;
    set_line_width 1;
    sk |> List.iter (fun (v1, v2) ->
      draw_poly_line [| conv_vertex v1; conv_vertex v2 |]))

let draw_silhouette sil =
  with_canvas (fun () ->
    set_color white;
    set_line_width 1;
    sil |> List.iter (fun poly ->
      poly |> List.iter (fun v ->
        plots [| conv_vertex v |])))

let draw_poly (p: polygon) =
  with_canvas (fun () ->
    set_color white;
    set_line_width 1;
    List.combine p (rotate p) |> List.iter (fun (v1, v2) ->
      draw_poly_line [| conv_vertex v1; conv_vertex v2 |]))

let draw_line_inner (l: line) =
  let open Num in
  let (x1, y1, x2, y2) =
    if l.a =/ num_0 then
      let y0 = (minus_num l.c) // l.b in
      let x1 = num_0 in
      let x2 = num_1 in
      (x1, y0, x2, y0)
    else if l.b =/ num_0 then
      let x0 = (minus_num l.c) // l.a in
      let y1 = num_0 in
      let y2 = num_1 in
      (x0, y1, x0, y2)
    else
      let x1 = num_of_int 0 in
      let x2 = num_of_int 1 in
      let y1 = Geometry.get_line_y_by_x l x1 in
      let y2 = Geometry.get_line_y_by_x l x2 in
      (x1, y1, x2, y2)
  in
  draw_poly_line [| conv_vertex (x1, y1); conv_vertex (x2, y2) |]

let draw_line (l: line) =
  with_canvas (fun () ->
    set_color white;
    set_line_width 1;
    draw_line_inner l)

let draw_line_and_two_vertexes (l: line) v1 v2 =
  with_canvas (fun () ->
    set_color white;
    set_line_width 1;
    let open Num in
    let x1 = num_of_int 0 in
    let x2 = num_of_int 1 in
    let y1 = Geometry.get_line_y_by_x l x1 in
    let y2 = Geometry.get_line_y_by_x l x2 in
    draw_poly_line [| conv_vertex (x1, y1); conv_vertex (x2, y2) |];
    draw_poly_line [| conv_vertex v1; conv_vertex v2 |])

let draw_solution (target: polygon) (sol: Solution.t) =
  with_canvas (fun () ->
    set_color red;
    set_line_width 1;
    List.combine target (rotate target) |> List.iter (fun (v1, v2) ->
      draw_poly_line [| conv_vertex v1; conv_vertex v2 |]);

    set_color white;
    set_line_width 1;
    let poly = sol.dest |> convex_hull in
    List.combine poly (rotate poly) |> List.iter (fun (v1, v2) ->
      draw_poly_line [| conv_vertex v1; conv_vertex v2 |]);

    set_color green;
    set_line_width 1;
    sol.flips |> List.iter draw_line_inner)
