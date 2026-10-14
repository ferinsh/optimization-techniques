# Algorithm: Simplex Method for Maximization

**Input:** Objective function coefficients `C`, constraint coefficient matrix `A`, and right-hand-side values `B`.

**Output:** Optimal solution, maximum objective value, or problem status.

## Step-by-Step Algorithm

1. **Start.**

2. **Read the Linear Programming Problem (LPP).**
   - Read the objective function to be maximized:

     $$Z = c_1x_1 + c_2x_2 + \cdots + c_nx_n$$

   - Read all constraints in the form:

     $$Ax \leq B$$

   - Ensure that all decision variables are non-negative and all right-hand-side values are non-negative.

3. **Convert Constraints into Equations.**
   - Add one slack variable to each constraint.
   - Use the slack variables as the initial basic variables.

4. **Construct the Initial Simplex Tableau.**
   - Enter the coefficients of the decision variables and slack variables.
   - Enter the right-hand-side values.
   - Construct the objective row using the negative coefficients of the objective function and zeros for the slack variables.

5. **Check the Optimality Condition.**
   - Examine the objective row.
   - If all coefficients in the variable columns are non-negative within a specified numerical tolerance, proceed to Step 10.
   - Otherwise, continue to Step 6.

6. **Select the Entering Variable.**
   - Choose a variable whose coefficient in the objective row is negative.
   - Select the first eligible variable from left to right to help prevent cycling.

7. **Select the Leaving Variable.**
   - Calculate the ratio for each constraint row:

     $$\text{Ratio}_i = \frac{B_i}{a_{ij}}$$

     where `a_ij > 0` is the coefficient of the entering variable in row `i`.

   - Ignore rows where `a_ij <= 0`.
   - Select the row with the smallest non-negative ratio. The basic variable in that row becomes the leaving variable.
   - If no eligible row exists, declare the problem unbounded and stop.

8. **Perform the Pivot Operation.**
   - Divide the pivot row by the pivot element to make the pivot element equal to 1.
   - Use elementary row operations to make every other entry in the entering variable's column equal to 0.
   - Update the basic variable associated with the pivot row.

9. **Repeat the Simplex Iteration.**
   - Return to Step 5.
   - Continue until the optimality condition is satisfied or the iteration limit is reached.

10. **Determine the Optimal Solution.**
    - Assign the right-hand-side value of each basic decision variable to that variable.
    - Assign zero to every non-basic decision variable.
    - Calculate the maximum objective function value:

      $$Z_{\max} = \sum_{j=1}^{n} c_jx_j$$

11. **Display the Results.**
    - Problem status.
    - Optimal values of the decision variables.
    - Maximum objective function value.
    - Number of iterations performed.
    - Simplex tableau for each iteration.

12. **Stop.**
