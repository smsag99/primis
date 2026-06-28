module alu(input [7:0] a, b, input [1:0] op, output reg [7:0] y);
    always @(*) begin
        case(op)
            2'b00: y = a + b;   // ADD
            2'b01: y = a - b;   // SUB
            2'b10: y = a | b;   // OR
            2'b11: y = a & b;   // AND
            default: y = 8'b0;  // Default case to avoid latches, though not strictly necessary for full case
        endcase
    end
endmodule