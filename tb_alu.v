// Golden testbench — fixed verification contract. Agents must NOT edit this.
`timescale 1ns/1ps
module tb_alu;
  reg  [7:0] a, b;
  reg  [1:0] op;
  wire [7:0] y;

  alu dut(.a(a), .b(b), .op(op), .y(y));

  integer errors = 0;
  task check(input [7:0] exp);
    begin
      #1;
      if (y !== exp) begin
        $display("FAIL: a=%0d b=%0d op=%0d -> y=%0d (expected %0d)", a,b,op,y,exp);
        errors = errors + 1;
      end
    end
  endtask

  initial begin
    a=8'd10; b=8'd3; op=2'b00; check(8'd13); // ADD
    a=8'd10; b=8'd3; op=2'b01; check(8'd7);  // SUB
    a=8'hF0; b=8'h0F; op=2'b10; check(8'hFF); // OR
    a=8'hF0; b=8'h3C; op=2'b11; check(8'h30); // AND
    if (errors == 0) $display("ALL_TESTS_PASSED");
    else $display("TESTS_FAILED: %0d", errors);
    $finish;
  end
endmodule
