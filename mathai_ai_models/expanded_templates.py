"""
Enhanced Template Library for Math Question Generation
Provides 10x more variety than original templates with expanded topics
"""

from typing import Dict, List, Tuple

# Template format: {a}, {b}, {c}, etc. will be replaced with smart numbers
# NUM token for backward compatibility (will be replaced by smart number generator)

EXPANDED_TEMPLATES = {
    "algebra": {
        "easy": {
            (1, 5): [
                # Basic linear equations (one-step)
                "Solve for x: x + {a} = {b}",
                "Find x if x - {a} = {b}",
                "If x + {a} = {b}, what is x?",
                "What value of x makes x + {a} = {b} true?",
                "{a} + x = {b}. Find x.",
                "x - {a} = {b}. What is x?",
                "Solve: {a} + x = {b}",
                "Find the value of x: x + {a} = {b}",
                
                # Basic multiplication/division
                "Solve for x: {a}x = {b}",
                "Find x if {a}x = {b}",
                "If {a} times x equals {b}, what is x?",
                "{a}x = {b}. Find x.",
                "What number times {a} equals {b}?",
                "Solve: x ÷ {a} = {b}",
                "If x divided by {a} is {b}, find x.",
                
                # Word problems (simple addition/subtraction)
                "Sarah has {a} apples. She gets {b} more. How many apples does she have now?",
                "Tom had {a} toys. He gave away {b} toys. How many toys does he have left?",
                "A toy costs ${a}. If you pay with ${b}, how much change do you get?",
                "There are {a} students in class. {b} more students join. How many total?",
                "A book has {a} pages. You read {b} pages. How many pages are left?",
                "You have {a} candies. You eat {b} candies. How many remain?",
                "A box has {a} crayons. You buy {b} more. How many total?",
                "Mom bakes {a} cookies. The family eats {b}. How many cookies are left?",
                
                # Simple patterns
                "What number comes next: {a}, {b}, {c}, ___?",
                "Continue the pattern: {a}, {b}, {c}, ___",
                "Fill in the blank: {a}, {b}, ___, {d}",
                
                # Comparison
                "Which is greater: {a} or {b}?",
                "What is {a} more than {b}?",
                "What is {a} less than {b}?",
            ],
            
            (6, 9): [
                # Two-step equations
                "Solve: {a}x + {b} = {c}",
                "Find x if {a}x - {b} = {c}",
                "Solve for x: {a}x + {b} = {c}",
                "If {a}x + {b} = {c}, what is x?",
                "{a}x - {b} = {c}. Find x.",
                "Solve: {b} + {a}x = {c}",
                "Find the value of x: {a}x + {b} = {c}",
                "What value of x satisfies {a}x - {b} = {c}?",
                
                # Equations with fractions
                "Solve: x/{a} = {b}",
                "Find x if x/{a} + {b} = {c}",
                "Solve for x: {a}/x = {b}",
                
                # Equations with parentheses  
                "Solve: {a}(x + {b}) = {c}",
                "Find x if {a}(x - {b}) = {c}",
                "Solve for x: {a}(x + {b}) = {c}",
                "{a}(x - {b}) = {c}. What is x?",
                
                # Word problems (money, rates)
                "A shirt costs ${a}. With a ${b} discount, the price is ${c}. Find the original price.",
                "John earns ${a} per hour. He works {b} hours. How much does he earn?",
                "A phone plan costs ${a} per month plus ${b} per GB. For {c} GB, what's the total cost?",
                "Tickets cost ${a} for adults and ${b} for children. A family of {c} people pays ${d}. How many children?",
                
                # Perimeter/area basics
                "A rectangle has length {a} cm and width {b} cm. Find the perimeter.",
                "A square has perimeter {a} cm. What is the length of one side?",
                "A rectangle has area {a} cm² and width {b} cm. Find the length.",
            ],
            
            (10, 12): [
                # Multi-step linear equations
                "Solve: {a}({b}x + {c}) + {d} = {e}",
                "Find x if {a}x + {b} = {c}x + {d}",
                "Solve for x: {a}({b} - x) = {c}",
                "{a}x - {b} = {c}x + {d}. Find x.",
                "Solve: {a}(x + {b}) - {c} = {d}x",
                
                # Equations with multiple variables
                "If {a}x + {b}y = {c} and x = {d}, find y.",
                "Solve for x: {a}x + {b} = {c}y, given y = {d}",
                
                # Ratio and proportion
                "If {a}:{b} = x:{c}, find x.",
                "Solve: x/{a} = {b}/{c}",
                
                # Word problems (advanced)
                "A number increased by {a}% is {b}. Find the original number.",
                "Two numbers sum to {a}. Their difference is {b}. Find the larger number.",
                "The sum of three consecutive integers is {a}. Find the middle integer.",
                "A car travels {a} km in {b} hours. At this rate, how long to travel {c} km?",
            ]
        },
        
        "medium": {
            (1, 5): [
                # Two-step problems
                "Solve: {a}x + {b} = {c}",
                "Find x if {a}x - {b} = {c}",
                "If {a} times x minus {b} equals {c}, find x.",
                "Solve for x: {a}x = {b} + {c}",
                "{a}x + {b} = {c}. What is x?",
                
                # Mixed operations
                "What is {a} × {b} + {c}?",
                "Calculate: {a} × {b} - {c}",
                "Find: ({a} + {b}) × {c}",
                "Solve: {a} × (x + {b}) = {c}",
                
                # Word problems
                "A bag has {a} red marbles and {b} blue marbles. If you add {c} more red marbles, how many red marbles total?",
                "Pizza costs ${a}. You buy {b} pizzas. How much change from ${c}?",
                "A train travels {a} km per hour for {b} hours. How far does it go?",
            ],
            
            (6, 9): [
                # Variable on both sides
                "Solve: {a}x + {b} = {c}x + {d}",
                "Find x if {a}x - {b} = {c}x - {d}",
                "{a}(x + {b}) = {c}x + {d}. Solve for x.",
                "Solve: {a}x + {b} = {c}(x - {d})",
                
                # Equations with fractions
                "Solve: {a}x/{b} + {c} = {d}",
                "Find x if x/{a} + x/{b} = {c}",
                "Solve: {a}/x + {b} = {c}",
                
                # Distributive property
                "Solve: {a}({b}x + {c}) = {d}",
                "Expand and solve: {a}(x + {b}) + {c}(x - {d}) = {e}",
                "{a}({b} - x) + {c} = {d}. Find x.",
                
                # Word problems (rates, ratios)
                "Two numbers have ratio {a}:{b}. Their sum is {c}. Find the larger number.",
                "A recipe needs {a} cups flour for {b} servings. How much for {c} servings?",
                "If {a} workers complete a job in {b} days, how long for {c} workers?",
                "Distance between two cities is {a} km. A car travels at {b} km/h. How long does it take?",
            ],
            
            (10, 12): [
                # Quadratic equations (factoring)
                "Solve: x² + {a}x + {b} = 0",
                "Find x if x² - {a}x + {b} = 0",
                "Solve by factoring: x² + {a}x + {b} = 0",
                "x² - {a} = 0. Find all values of x.",
                
                # Systems of equations
                "Solve: {a}x + {b}y = {c} and {d}x + {e}y = {f}",
                "Find x and y: {a}x + {b}y = {c}, {d}x - {e}y = {f}",
                
                # Absolute value
                "Solve: |x + {a}| = {b}",
                "Find x if |{a}x - {b}| = {c}",
                
                # Word problems (optimization, mixture)
                "Tickets sold: {a} adult tickets at ${b} and {c} child tickets at ${d}. Total revenue: ${e}. Find the number of adult tickets.",
                "A {a}% salt solution is mixed with {b} liters of {c}% solution. Result is {d} liters of what concentration?",
            ]
        },
        
        "hard": {
            (1, 5): [
                # Multi-step with parentheses
                "Solve: {a}(x + {b}) = {c}",
                "Find x if {a}(x - {b}) + {c} = {d}",
                "{a}({b} + x) - {c} = {d}. What is x?",
                
                # Three-step problems
                "Solve: {a}x + {b} = {c}x - {d}",
                "Find x if {a}(x + {b}) = {c}(x - {d})",
                
                # Word problems (multi-step)
                "Mom buys {a} apples at ${b} each and {c} oranges at ${d} each. She pays with ${e}. What is her change?",
                "A box has {a} red balls and {b} blue balls. After adding {c} red balls and removing {d} blue balls, how many balls total?",
            ],
            
            (6, 9): [
                # Complex equations
                "Solve: {a}({b}x + {c}) + {d}(x - {e}) = {f}",
                "Find x if {a}x/{b} + {c}x/{d} = {e}",
                "Solve: ({a}x + {b})/({c}) = {d}",
                "{a}(x - {b}) = {c}({d} - x). Find x.",
                
                # Equations with multiple fractions
                "Solve: {a}/x + {b}/x = {c}",
                "Find x if x/{a} - x/{b} = {c}",
                
                # Word problems (complex rates)
                "Pipe A fills a tank in {a} hours. Pipe B fills it in {b} hours. Together, how long?",
                "Train A leaves at 8am traveling {a} km/h. Train B leaves at 9am traveling {b} km/h. When do they meet?",
                "A job takes {a} hours for person A and {b} hours for person B. Working together, how long?",
            ],
            
            (10, 12): [
                # Quadratic (quadratic formula)
                "Solve: {a}x² + {b}x + {c} = 0",
                "Find x if {a}x² - {b}x + {c} = 0 (use quadratic formula)",
                "x² + {a}x + {b} = {c}. Solve for x.",
                
                # Complex systems
                "Solve: {a}x + {b}y = {c}, {d}x + {e}y = {f}",
                "Find x and y: {a}x - {b}y = {c}, {d}x + {e}y = {f}",
                "Solve the system: x + {a}y = {b}, {c}x - y = {d}",
                
                # Exponential/logarithmic (basic)
                "If {a}^x = {b}, find x.",
                "Solve: {a}^(x+{b}) = {c}",
                
                # Word problems (complex)
                "Investment of ${a} grows at {b}% annually. How long to reach ${c}?",
                "Population of {a} increases {b}% yearly. What will it be in {c} years?",
                "A radioactive substance decays {a}% per year. After {b} years, {c} grams remain. Find initial amount.",
            ]
        }
    },
    
    "geometry": {
        "easy": {
            (1, 5): [
                # Basic shapes - area
                "Find the area of a square with side {a} cm.",
                "What is the area of a rectangle with length {a} cm and width {b} cm?",
                "A square has side length {a} meters. What is its area?",
                "Calculate the area of a rectangle {a} cm by {b} cm.",
                
                # Basic shapes - perimeter
                "Find the perimeter of a square with side {a} cm.",
                "What is the perimeter of a rectangle with sides {a} cm and {b} cm?",
                "A square has perimeter {a} cm. What is the side length?",
                "Rectangle has length {a} m and width {b} m. Find the perimeter.",
                
                # Counting faces/edges
                "How many faces does a cube have?",
                "A rectangular prism has {a} faces. How many edges does it have?",
                "Count the vertices of a triangular pyramid.",
                
                # Simple volume
                "A cube has edge {a} cm. What is its volume?",
                "Find the volume of a box {a} cm long, {b} cm wide, {c} cm tall.",
            ],
            
            (6, 9): [
                # Circles
                "Find the area of a circle with radius {a} cm. Use π ≈ 3.14.",
                "What is the circumference of a circle with radius {a} cm? (π ≈ 3.14)",
                "A circle has diameter {a} m. Find its area. (π ≈ 3.14)",
                "Circle with radius {a} cm. What is its circumference? Use π ≈ 3.14.",
                
                # Volume of rectangular prisms
                "Find the volume of a cube with edge {a} cm.",
                "What is the volume of a box {a} × {b} × {c} cm? ",
                "Rectangular prism: length {a} cm, width {b} cm, height {c} cm. Find volume.",
                
                # Pythagorean theorem (basic)
                "A right triangle has legs {a} cm and {b} cm. Find the hypotenuse.",
                "Right triangle: one leg is {a} m, hypotenuse is {b} m. Find the other leg.",
                
                # Surface area (simple)
                "Find the surface area of a cube with edge {a} cm.",
                "What is the surface area of a box {a} × {b} × {c} cm?",
            ],
            
            (10, 12): [
                # Sphere volume/surface area
                "Find the volume of a sphere with radius {a} cm. Use π ≈ 3.14.",
                "What is the surface area of a sphere with radius {a} cm? (π ≈ 3.14)",
                
                # Cylinder
                "Find the volume of a cylinder: radius {a} cm, height {b} cm. Use π ≈ 3.14.",
                "Cylinder with radius {a} m and height {b} m. Find surface area. (π ≈ 3.14)",
                
                # Cone
                "Find the volume of a cone: radius {a} cm, height {b} cm. Use π ≈ 3.14.",
                
                # Coordinate geometry
                "Find the distance between points ({a}, {b}) and ({c}, {d}).",
                "What is the midpoint of ({a}, {b}) and ({c}, {d})?",
                "Find the slope of the line through ({a}, {b}) and ({c}, {d}).",
            ]
        },
        
        "medium": {
            (1, 5): [
                # Composite shapes
                "A rectangle {a} cm by {b} cm has a {c} cm square cut from it. Find remaining area.",
                "Two squares with sides {a} cm and {b} cm. What is their combined area?",
                
                # Real-world applications
                "A room is {a} m by {b} m. Tiles are {c} cm squares. How many tiles needed?",
                "Fence a yard {a} m by {b} m. Fencing costs ${c} per meter. Total cost?",
                "Paint a wall {a} m by {b} m. One can covers {c} m². How many cans needed?",
            ],
            
            (6, 9): [
                # Combined shapes
                "Find the area of a rectangle {a} × {b} cm with a semicircle (diameter {a}) on top. Use π ≈ 3.14.",
                "A rectangular field {a} m by {b} m has circular pond diameter {c} m. Find remaining area. (π ≈ 3.14)",
                
                # Volume problems
                "A water tank (cube, edge {a} m) is {b}% full. How many liters? (1 m³ = 1000 L)",
                "Box {a} × {b} × {c} cm filled with {d} cm cubes. How many cubes fit?",
                
                # Surface area
                "Find surface area of rectangular prism {a} × {b} × {c} cm.",
                "Cylinder radius {a} cm, height {b} cm. Find total surface area. (π ≈ 3.14)",
                
                # Pythagorean theorem applications
                "A ladder {a} m long leans against wall, base {b} m from wall. How high up the wall?",
                "Rectangle has diagonal {a} cm and width {b} cm. Find the length.",
            ],
            
            (10, 12): [
                # Complex volume
                "Hemisphere radius {a} cm placed on cylinder radius {a} cm height {b} cm. Find total volume. (π ≈ 3.14)",
                "Cone (radius {a} cm, height {b} cm) fits in cylinder (same dimensions). Find volume difference. (π ≈ 3.14)",
                
                # Optimization
                "Rectangle has perimeter {a} cm. What dimensions give maximum area?",
                "Box with square base. Volume {a} cm³. Minimize surface area. Find dimensions.",
                
                # Trigonometry in triangles
                "Right triangle: angle {a}°, adjacent side {b} cm. Find opposite side.",
                "From point {a} m from building base, angle of elevation is {b}°. Find building height.",
                
                # Coordinate geometry
                "Find area of triangle with vertices ({a},{b}), ({c},{d}), ({e},{f}).",
                "Circle center ({a},{b}), radius {c}. Does point ({d},{e}) lie inside?",
            ]
        },
        
        "hard": {
            (1, 5): [
                # Multi-step area
                "L-shaped room: {a} m × {b} m with {c} m × {d} m section. Find area.",
                "Square {a} cm with {b} circles diameter {c} cm cut out. Find remaining area. (π ≈ 3.14)",
                
                # Cost calculations
                "Tile floor {a} m × {b} m. Tiles {c} cm squares cost ${d} each. Total cost?",
                "Garden {a} m × {b} m needs {c} cm topsoil. Soil is ${d} per cubic meter. Cost?",
            ],
            
            (6, 9): [
                # Complex surface area
                "Open-top box from {a} cm × {b} cm cardboard. Cut {c} cm squares from corners, fold. Find surface area.",
                "Cylinder radius {a} cm, height {b} cm, with hemisphere radius {a} cm on top. Find total surface area. (π ≈ 3.14)",
                
                # Volume optimization
                "Cylinder volume {a} cm³, height {b} cm. Find radius. (π ≈ 3.14)",
                "Cone and cylinder have equal volume and radius {a} cm. Cone height {b} cm. Find cylinder height.",
                
                # Advanced Pythagorean
                "Right triangle hypotenuse {a} cm, one leg {b} times the other. Find both legs.",
                "Isosceles triangle: two sides {a} cm, base {b} cm. Find the height.",
            ],
            
            (10, 12): [
                # Sphere inscribed/circumscribed
                "Sphere inscribed in cube edge {a} cm. Find sphere volume. (π ≈ 3.14)",
                "Cube inscribed in sphere radius {a} cm. Find cube edge length.",
                "Sphere radius {a} cm. Find volume of inscribed cube. (π ≈ 3.14)",
                
                # Complex 3D geometry
                "Regular hexagonal prism: side {a} cm, height {b} cm. Find volume.",
                "Truncated cone: top radius {a} cm, bottom radius {b} cm, height {c} cm. Find volume. (π ≈ 3.14)",
                
                # Advanced coordinate geometry  
                "Find equation of circle through ({a},{b}), ({c},{d}), ({e},{f}).",
                "Parabola y = x². Find area between curve and line y = {a} from x = 0 to x = {b}.",
                
                # Trigonometric applications
                "Triangle sides {a} cm, {b} cm, angle {c}° between them. Find third side (law of cosines).",
                "Triangle sides {a}, {b}, {c} cm. Find largest angle.",
            ]
        }
    },
    
    "arithmetic": {
        "easy": {
            (1, 5): [
                "What is {a} + {b}?",
                "Calculate: {a} - {b}",
                "Find: {a} + {b} + {c}",
                "What is {a} - {b} - {c}?",
                "{a} plus {b} equals what?",
                "Subtract {b} from {a}.",
                "Add {a} and {b}.",
                "{a} minus {b} is?",
                
                # Multiplication basics
                "What is {a} × {b}?",
                "Calculate: {a} times {b}",
                "Find: {a} × {b}",
                "{a} multiplied by {b} equals?",
                
                # Division basics
                "What is {a} ÷ {b}?",
                "Calculate: {a} divided by {b}",
                "Find: {a} ÷ {b}",
                "Divide {a} by {b}.",
                
                # Word problems
                "You have {a} candies. You get {b} more. How many now?",
                "There were {a} birds. {b} flew away. How many remain?",
                "{a} children share {b} cookies equally. How many each?",
            ],
            
            (6, 9): [
                # Multi-digit operations
                "Calculate: {a} + {b} + {c}",
                "Find: {a} - {b} + {c}",
                "What is {a} × {b} + {c}?",
                "{a} × {b} - {c} = ?",
                
                # Order of operations (basic)
                "Calculate: ({a} + {b}) × {c}",
                "Find: {a} × ({b} + {c})",
                "What is ({a} - {b}) × {c}?",
                "{a} × {b} + {c} × {d} = ?",
                
                # Fractions (basic)
                "What is {a}/{b} + {c}/{d}?",
                "Calculate: {a}/{b} - {c}/{d}",
                "Find: {a}/{b} × {c}/{d}",
                "What is {a}/{b} ÷ {c}/{d}?",
                
                # Decimals
                "Calculate: {a}.{b} + {c}.{d}",
                "What is {a}.{b} - {c}.{d}?",
                "Find: {a}.{b} × {c}",
            ],
            
            (10, 12): [
                # Complex fractions
                "Simplify: {a}/{b} + {c}/{d} - {e}/{f}",
                "Calculate: ({a}/{b}) × ({c}/{d}) ÷ ({e}/{f})",
                "Find: {a}/{b} ÷ {c}/{d} + {e}/{f}",
                
                # Decimals with operations
                "Calculate: {a}.{b} × {c}.{d}",
                "What is {a}.{b} ÷ {c}.{d}?",
                "Find: ({a}.{b} + {c}.{d}) × {e}",
                
                # Percentages
                "What is {a}% of {b}?",
                "Find {a}% of {b}",
                "{a} is what percent of {b}?",
                "If {a}% of a number is {b}, find the number.",
            ]
        },
        
        "medium": {
            (1, 5): [
                "Calculate: {a} + {b} - {c}",
                "What is {a} × {b} + {c}?",
                "Find: ({a} + {b}) × {c}",
                "{a} × {b} - {c} = ?",
                
                # Two-step word problems
                "You buy {a} items at ${b} each. You pay with ${c}. What is your change?",
                "A box has {a} red balls and {b} blue balls. After adding {c} red balls, how many total?",
            ],
            
            (6, 9): [
                # Complex operations
                "Calculate: {a} × {b} + {c} × {d}",
                "What is ({a} + {b}) × ({c} - {d})?",
                "Find: {a} × {b} ÷ {c} + {d}",
                
                # Fractions and mixed numbers
                "What is {a} {b}/{c} + {d} {e}/{f}?",
                "Calculate: {a}/{b} × {c}/{d}",
                "Find: {a} {b}/{c} - {d} {e}/{f}",
                
                # Percentage problems
                "Increase {a} by {b}%",
                "Decrease {a} by {b}%",
                "{a} increased by {b}% is what?",
                "After a {a}% discount, price is ${b}. What was original price?",
            ],
            
            (10, 12): [
                # Complex percentage
                "{a}% of a number is {b}. Find the number.",
                "If {a}% of x is {b}, what is {c}% of x?",
                "Price increases {a}%, then decreases {b}%. Net change?",
                
                # Ratios and proportions
                "If {a}:{b} = x:{c}, find x.",
                "Ratio of boys to girls is {a}:{b}. There are {c} boys. How many girls?",
                
                # Complex calculations
                "Calculate: ({a}/{b} + {c}/{d}) × ({e}/{f} - {g}/{h})",
                "Find: {a}.{b} × {c}.{d} + {e}.{f}",
            ]
        },
        
        "hard": {
            (1, 5): [
                "Calculate: {a} ÷ {b} + {c} × {d}",
                "What is ({a} × {b}) ÷ ({c} + {d})?",
                "Find: {a} × {b} + {c} ÷ {d}",
                
                # Multi-step word problems
                "Store has {a} boxes with {b} apples each. Sells {c} apples. How many left?",
                "{a} students in {b} groups. Each group gets {c} pencils. How many total pencils?",
            ],
            
            (6, 9): [
                # Complex mixed operations
                "Calculate: {a}/{b} of {c}/{d} of {e}",
                "What is ({a}/{b} + {c}/{d}) × ({e}/{f})?",
                "Find: {a}.{b} × ({c}.{d} + {e}.{f})",
                
                # Percentage chains
                "Price ${a}, increases {b}%, then decreases {c}%. Final price?",
                "{a} increased by {b}%, result decreased by {c}%. Final value?",
                
                # Complex word problems
                "{a}% of students are boys. {b}% of boys play sports. If {c} students total, how many boys play sports?",
            ],
            
            (10, 12): [
                # Advanced percentage
                "If {a}/{b} of a number is {c}, what is {d}/{e} of it?",
                "Population {a} increases {b}% first year, {c}% second year. Final population?",
                
                # Complex rational operations
                "Simplify: ({a}/{b} ÷ {c}/{d}) × ({e}/{f} + {g}/{h})",
                "Calculate: ({a} {b}/{c} × {d} {e}/{f}) ÷ {g}",
                
                # Scientific notation (implied)
                "What is {a} × 10^{b} + {c} × 10^{d}?",
                "Calculate: ({a} × 10^{b}) ÷ ({c} × 10^{d})",
            ]
        }
    },
    
    "statistics": {
        "easy": {
            (1, 5): [
                # Data collection and basic counting
                "Count the objects: {a} red, {b} blue, {c} green. How many total?",
                "A group has {a} boys and {b} girls. How many children total?",
                "Survey results: {a} like pizza, {b} like burgers. How many voted?",
                "Tally marks show {a} votes for A, {b} for B. Which has more?",
                
                # Simple data interpretation
                "Bar chart shows: Monday {a} books, Tuesday {b} books. Which day had more?",
                "Pictograph: ⭐⭐⭐ = {a} stars per symbol. If there are {b} symbols, how many total stars?",
                "Table shows scores: {a}, {b}, {c}. What is the highest score?",
                "Which is the most common: {a} appears {b} times, {c} appears {d} times?",
            ],
            
            (6, 9): [
                # Mean (average)
                "Find the mean of: {a}, {b}, {c}",
                "Calculate the average: {a}, {b}, {c}, {d}",
                "What is the mean of {a}, {b}, {c}, {d}, {e}?",
                "Five students scored {a}, {b}, {c}, {d}, {e}. Find the average score.",
                
                # Median
                "Find the median of: {a}, {b}, {c}, {d}, {e}",
                "What is the median value: {a}, {b}, {c}?",
                "Data set: {a}, {b}, {c}, {d}, {e}, {f}, {g}. Find the median.",
                
                # Mode
                "Find the mode: {a}, {a}, {b}, {c}, {a}",
                "What value appears most often: {a}, {b}, {b}, {c}, {b}, {d}?",
                "Data: {a}, {b}, {a}, {c}, {a}, {b}. What is the mode?",
                
                # Range
                "Find the range of: {a}, {b}, {c}, {d}",
                "Data set: {a}, {b}, {c}, {d}, {e}. What is the range?",
                "Highest value is {a}, lowest is {b}. Find the range.",
            ],
            
            (10, 12): [
                # Mean, median, mode combined
                "Data: {a}, {b}, {c}, {d}, {e}. Find mean, median, and mode.",
                "Calculate mean and median for: {a}, {b}, {c}, {d}, {e}, {f}",
                "Find the range and mean: {a}, {b}, {c}, {d}, {e}",
                
                # Weighted average
                "Test 1 (weight {a}%): score {b}. Test 2 (weight {c}%): score {d}. Find weighted average.",
                "{a} items at ${b} each, {c} items at ${d} each. Find average price per item.",
                
                # Standard deviation (basic concept)
                "Data: {a}, {b}, {c}. Mean is {d}. Find the deviations from the mean.",
                "Values are {a}, {b}, {c}, {d}. Which value is furthest from the mean?",
                
                # Data analysis
                "Frequency table: Value {a} appears {b} times, value {c} appears {d} times. Find mean.",
                "Grouped data: {a}-{b} range has {c} values, {d}-{e} range has {f} values. Estimate mean.",
            ]
        },
        
        "medium": {
            (1, 5): [
                # Data comparison
                "Group A: {a}, {b}, {c}. Group B: {d}, {e}, {f}. Which has higher mean?",
                "Last week average {a}, this week average {b}. What is the change?",
                "Compare ranges: Set A ({a}, {b}, {c}) vs Set B ({d}, {e}, {f})",
            ],
            
            (6, 9): [
                # Quartiles and percentiles
                "Find the first quartile (Q1) of: {a}, {b}, {c}, {d}, {e}, {f}, {g}",
                "Data: {a}, {b}, {c}, {d}, {e}. Find Q1, Q2 (median), and Q3.",
                "What is the interquartile range (IQR) of: {a}, {b}, {c}, {d}, {e}, {f}, {g}, {h}?",
                
                # Box plots interpretation
                "Box plot shows: Min={a}, Q1={b}, Median={c}, Q3={d}, Max={e}. Find IQR.",
                "Five-number summary: {a}, {b}, {c}, {d}, {e}. What is the range?",
                
                # Outliers
                "Data: {a}, {b}, {c}, {d}, {e}. Is {f} an outlier? (Use IQR method)",
                "Q1={a}, Q3={b}. Calculate lower and upper outlier boundaries.",
                
                # Variance (introduction)
                "Mean is {a}. Deviations are: {b}, {c}, {d}. Find sum of squared deviations.",
                "Data: {a}, {b}, {c}. Mean = {d}. Calculate variance.",
            ],
            
            (10, 12): [
                # Standard deviation calculation
                "Data: {a}, {b}, {c}, {d}, {e}. Calculate standard deviation.",
                "Mean = {a}, variance = {b}. Find standard deviation.",
                "Scores: {a}, {b}, {c}, {d}. Find mean and standard deviation.",
                
                # Correlation basics
                "As x increases from {a} to {b}, y decreases from {c} to {d}. Is correlation positive or negative?",
                "Data pairs: ({a},{b}), ({c},{d}), ({e},{f}). Does y increase or decrease as x increases?",
                
                # Sampling
                "Population of {a}, sample of {b} selected. What percentage is sampled?",
                "Survey {a} people from population {b}. Is this sample representative? Margin of error ±{c}%.",
                
                # Probability distributions (basic)
                "Normal distribution: mean={a}, std dev={b}. What is the z-score for value {c}?",
                "Data is normally distributed with mean {a} and std dev {b}. Approximately what % within 1 std dev?",
            ]
        },
        
        "hard": {
            (1, 5): [
                # Multi-step statistics
                "Data: {a}, {b}, {c}, {d}. Add value {e}. How does the mean change?",
                "Original mean {a} with {b} values. Add {c}. What is new mean?",
                "Remove outlier {a} from data: {a}, {b}, {c}, {d}. How does median change?",
            ],
            
            (6, 9): [
                # Complex measures
                "Combined dataset: Set A (mean={a}, n={b}) and Set B (mean={c}, n={d}). Find overall mean.",
                "Class A: {a} students, average {b}. Class B: {c} students, average {d}. Combined average?",
                
                # Data transformation
                "Original data: {a}, {b}, {c}. Each value increased by {d}. What is new mean?",
                "Data: {a}, {b}, {c}. Each value multiplied by {d}. How does std dev change?",
                
                # Missing value problems
                "Five numbers have mean {a}. Four numbers are {b}, {c}, {d}, {e}. Find the fifth number.",
                "Data set mean is {a}. Numbers are {b}, {c}, {d}, x. Find x.",
            ],
            
            (10, 12): [
                # Advanced standard deviation
                "Two data sets have same mean {a}. Set A std dev={b}, Set B std dev={c}. Which is more variable?",
                "Distribution A: mean={a}, std dev={b}. Distribution B: mean={c}, std dev={d}. Compare variability.",
                
                # Regression (basic)
                "Linear regression: y = {a}x + {b}. Predict y when x = {c}.",
                "Data points: ({a},{b}), ({c},{d}). Find slope of best fit line.",
                "Correlation coefficient r = {a}. Describe strength of relationship.",
                
                # Hypothesis testing (conceptual)
                "Sample mean={a}, population mean={b}, std error={c}. Is difference significant?",
                "95% confidence interval: [{a}, {b}]. Does it include hypothesized value {c}?",
            ]
        }
    },
    
    "probability": {
        "easy": {
            (1, 5): [
                # Simple probability (certain, impossible, likely)
                "A bag has {a} red balls and {b} blue balls. Are you certain to pick a red ball?",
                "Is it impossible to roll a {a} on a standard die?",
                "Which is more likely: rolling even or odd on a die?",
                "A coin is flipped. What are the possible outcomes?",
                
                # Basic probability fraction
                "A bag has {a} red and {b} blue marbles. What is the probability of picking red?",
                "In a class of {a} students, {b} are girls. What fraction are girls?",
                "A die has {a} sides. What is the probability of rolling {b}?",
                "Spinner has {a} equal sections: {b} red, {c} blue. Probability of red?",
                
                # Simple events
                "What is the probability of flipping heads on a coin?",
                "Probability of rolling a {a} on a die?",
                "Bag has {a} apples, {b} oranges. What is P(apple)?",
            ],
            
            (6, 9): [
                # Probability as fraction/decimal/percent
                "Convert probability {a}/{b} to decimal.",
                "Express {a}% as a probability fraction.",
                "Probability is 0.{a}. Express as a fraction.",
                "If P(event) = {a}/{b}, what is P(not event)?",
                
                # Complementary events
                "P(rain) = {a}/{b}. Find P(no rain).",
                "Probability of winning is {a}%. What is probability of not winning?",
                "If P(A) = 0.{a}, find P(not A).",
                
                # Two-event probability (basic)
                "Bag has {a} red, {b} blue balls. Pick one, replace it, pick again. P(both red)?",
                "Flip coin twice. What is P(two heads)?",
                "Roll die twice. Probability of getting {a} both times?",
                
                # Tree diagrams (simple)
                "Coin flip then die roll. How many possible outcomes?",
                "Two spinners: first has {a} sections, second has {b} sections. Total outcomes?",
            ],
            
            (10, 12): [
                # Compound probability (AND)
                "P(A) = {a}/{b}, P(B) = {c}/{d}. If independent, find P(A and B).",
                "Draw two cards with replacement. P(both aces) if deck has {a} aces and {b} total cards?",
                "Probability of rain Monday is {a}%, Tuesday is {b}%. P(rain both days) if independent?",
                
                # Compound probability (OR)
                "P(A) = {a}/{b}, P(B) = {c}/{d}. If mutually exclusive, find P(A or B).",
                "Roll a die. What is P(rolling {a} or {b})?",
                "Pick a card. P(heart or king)? Deck has {a} hearts, {b} kings, {c} cards total.",
                
                # Conditional probability (introduction)
                "Bag: {a} red, {b} blue balls. Pick one without replacement. P(second is red | first is red)?",
                "Class: {a} students total, {b} play sports, {c} play sports and music. P(music | sports)?",
                "Given P(A) = {a}/{b} and P(A and B) = {c}/{d}, find P(B | A).",
            ]
        },
        
        "medium": {
            (1, 5): [
                # Multiple events (basic)
                "Flip coin and roll die. P(heads and even number)?",
                "Bag: {a} red, {b} blue, {c} green balls. P(red or blue)?",
                "Spinner: {a} sections labeled 1-{a}. P(even number)?",
            ],
            
            (6, 9): [
                # Without replacement
                "Bag: {a} red, {b} blue balls. Pick two without replacement. P(both red)?",
                "Deck of {a} cards: {b} aces. Draw two without replacement. P(both aces)?",
                "Box: {a} red, {b} green balls. Pick two. P(one red, one green)?",
                
                # Dependent events
                "Jar: {a} white, {b} black marbles. Pick one, don't replace. Then pick another. P(white then black)?",
                "Cards: {a} total, {b} hearts. Draw two without replacement. P(both hearts)?",
                
                # Expected value (basic)
                "Game: win ${a} with probability {b}/{c}, win ${d} with probability {e}/{f}. Expected value?",
                "Die: pay ${a} to play. Win ${b} if roll {c}. Expected profit/loss?",
                "Lottery: {a} tickets sold, {b} prizes of ${c} each. Cost ${d} per ticket. Expected value?",
                
                # Permutations (introduction)
                "How many ways to arrange {a} books on a shelf?",
                "{a} people in a race. How many possible orders for 1st, 2nd, 3rd?",
                "Arrange letters A, B, C. How many arrangements?",
            ],
            
            (10, 12): [
                # Conditional probability
                "P(A|B) = {a}/{b}, P(B) = {c}/{d}. Find P(A and B).",
                "Survey: P(owns car) = {a}%, P(car and bike) = {b}%. Find P(bike | car).",
                "Disease test: P(positive | disease) = {a}%, P(disease) = {b}%. Find P(positive and disease).",
                
                # Combinations
                "Choose {a} items from {b} items. How many combinations?",
                "Committee of {a} people chosen from {b}. How many ways?",
                "Lottery: choose {a} numbers from {b}. How many combinations?",
                
                # Permutations vs Combinations
                "Select {a} people from {b} for a committee. Order matters or not?",
                "Arrange {a} out of {b} letters. How many permutations?",
                "Choose {a} toppings from {b} available. How many combinations?",
                
                # Binomial probability (introduction)
                "Flip coin {a} times. P(exactly {b} heads)?",
                "Multiple choice: {a} questions, {b} choices each. If guessing, P(exactly {c} correct)?",
            ]
        },
        
        "hard": {
            (1, 5): [
                # Complex scenarios
                "Bag A: {a} red, {b} blue. Bag B: {c} red, {d} blue. Pick bag randomly, then ball. P(red)?",
                "Two dice rolled. P(sum equals {a})?",
                "Three coins flipped. P(at least {a} heads)?",
            ],
            
            (6, 9): [
                # Conditional with multiple conditions
                "P(A) = {a}%, P(B) = {b}%, P(A and B) = {c}%. Find P(A | B).",
                "Medical test: sensitivity {a}%, specificity {b}%, prevalence {c}%. P(disease | positive)?",
                
                # Complex counting
                "Password: {a} letters then {b} digits. How many possible passwords?",
                "License plate: {a} letters, {b} numbers, {c} letters. Total combinations?",
                
                # Expected value with multiple outcomes
                "Game: P(win ${a}) = {b}%, P(win ${c}) = {d}%, P(lose ${e}) = {f}%. Expected value?",
                "Investment: {a}% chance gain ${b}, {c}% chance lose ${d}. Expected return?",
            ],
            
            (10, 12): [
                # Bayes' theorem
                "P(A) = {a}%, P(B|A) = {b}%, P(B|not A) = {c}%. Find P(A|B).",
                "Disease prevalence {a}%. Test: sensitivity {b}%, false positive rate {c}%. P(disease | positive)?",
                "Factory A produces {a}% of items, defect rate {b}%. Factory B: {c}% of items, {d}% defects. P(from A | defective)?",
                
                # Advanced combinations/permutations
                "How many {a}-letter words from {b} distinct letters (repetition allowed)?",
                "Committee: choose {a} from {b} people, but {c} and {d} cannot both serve. How many ways?",
                "Arrange {a} identical red balls and {b} identical blue balls. How many arrangements?",
                
                # Geometric and negative binomial (concepts)
                "Flip coin until heads. What is P(first heads on {a}th flip)?",
                "Success rate {a}%. Expected number of trials until first success?",
                "Continue until {a} successes. What is P(exactly {b} trials needed)?",
                
                # Joint probability distributions
                "X and Y independent. P(X={a}) = {b}%, P(Y={c}) = {d}%. Find P(X={a} and Y={c}).",
                "Joint probability table given. Find P(X={a}), P(Y={b}), P(X={a}|Y={b}).",
            ]
        }
    },
    
    "trigonometry": {
        "easy": {
            (6, 9): [
                # Basic angle relationships
                "Two angles are complementary. One is {a}°. Find the other.",
                "Supplementary angles sum to 180°. One is {a}°. Find the other.",
                "Triangle has angles {a}°, {b}°, and x°. Find x.",
                "Right triangle has one angle {a}°. Find the other acute angle.",
                
                # Angle types
                "Is {a}° an acute, obtuse, or right angle?",
                "Classify angle {a}°: acute, right, obtuse, or straight?",
                "Two angles sum to 90°. They are called _____ angles.",
                
                # Unit circle basics (special angles)
                "What is sin(0°)?",
                "Find cos(90°).",
                "What is tan(45°)?",
                "Calculate sin(90°).",
            ],
            
            (10, 12): [
                # Basic trig ratios in right triangles
                "Right triangle: opposite = {a}, hypotenuse = {b}. Find sin(θ).",
                "Right triangle: adjacent = {a}, hypotenuse = {b}. Find cos(θ).",
                "Right triangle: opposite = {a}, adjacent = {b}. Find tan(θ).",
                "If sin(θ) = {a}/{b}, and cos(θ) = {c}/{d}, find tan(θ).",
                
                # Special angle values
                "What is sin(30°)?",
                "Find cos(60°).",
                "Calculate tan(30°).",
                "What is sin(45°)?",
                "Find cos(45°).",
                "What is sin(60°)?",
                
                # Pythagorean identity (basic)
                "If sin(θ) = {a}/{b}, find cos(θ) using sin²θ + cos²θ = 1.",
                "Given cos(θ) = {a}/{b}, find sin(θ).",
            ]
        },
        
        "medium": {
            (6, 9): [
                # Solving for sides (SOH-CAH-TOA)
                "Right triangle: angle {a}°, adjacent side {b} cm. Find opposite side.",
                "Right triangle: angle {a}°, hypotenuse {b} m. Find opposite side.",
                "Right triangle: angle {a}°, opposite {b} cm. Find hypotenuse.",
                "Find height of building: angle of elevation {a}° from {b} m away.",
                
                # Angle of elevation/depression
                "From {a} m high, angle of depression to object is {b}°. How far is the object?",
                "Looking up at {a}° angle from {b} m away. How tall is the building?",
                "Ladder {a} m long makes {b}° angle with ground. How high up the wall?",
            ],
            
            (10, 12): [
                # Law of sines (introduction)
                "Triangle: angle A = {a}°, angle B = {b}°, side a = {c}. Find side b.",
                "Use law of sines: A = {a}°, B = {b}°, a = {c} cm. Find b.",
                
                # Law of cosines (introduction)
                "Triangle: sides {a}, {b} cm, included angle {c}°. Find third side.",
                "Sides a = {a}, b = {b}, c = {c}. Find angle C using law of cosines.",
                
                # Reciprocal functions
                "If sin(θ) = {a}/{b}, find csc(θ).",
                "Given cos(θ) = {a}/{b}, find sec(θ).",
                "If tan(θ) = {a}/{b}, find cot(θ).",
                
                # Multiple angle problems
                "Right triangle: one angle {a}°. Find sin({a}°), cos({a}°), tan({a}°).",
                "Given triangle with angles {a}°, {b}°, {c}°. Find all six trig functions for angle {a}°.",
            ]
        },
        
        "hard": {
            (10, 12): [
                # Trig identities
                "Prove: sin²(θ) + cos²(θ) = 1 when sin(θ) = {a}/{b}.",
                "Simplify: sin(θ)cos(θ)tan(θ)",
                "Verify: (1 + tan²θ) = sec²θ when tan(θ) = {a}/{b}.",
                "Prove: 1 + cot²θ = csc²θ",
                
                # Double angle formulas
                "If sin(θ) = {a}/{b}, find sin(2θ) using sin(2θ) = 2sin(θ)cos(θ).",
                "Given cos(θ) = {a}/{b}, find cos(2θ).",
                "Calculate tan(2θ) if tan(θ) = {a}/{b}.",
                
                # Solving trig equations
                "Solve for θ in [0°, 360°]: sin(θ) = {a}",
                "Find all θ where cos(θ) = {a}/{b} in [0°, 360°].",
                "Solve: 2sin(θ) + {a} = 0 for θ in [0°, 360°].",
                "Find θ: tan(θ) = {a} in [0°, 180°].",
                
                # Law of sines/cosines (complex)
                "Triangle: sides a = {a}, b = {b}, angle C = {c}°. Find all angles and side c.",
                "Given sides {a}, {b}, {c} cm. Find all three angles.",
                "Oblique triangle: A = {a}°, b = {b}, c = {c}. Find all remaining parts.",
                
                # Area formulas
                "Triangle: sides {a} and {b} cm, included angle {c}°. Find area.",
                "Use Heron's formula: sides {a}, {b}, {c}. Find area.",
                "Triangle: a = {a}, b = {b}, sin(C) = {c}/{d}. Find area.",
                
                # Unit circle and radians
                "Convert {a}° to radians.",
                "Convert {a}π/{b} radians to degrees.",
                "If θ = {a}π/{b}, find sin(θ), cos(θ), tan(θ).",
                
                # Advanced applications
                "A {a} m ladder leans at {b}° angle. Slides to {c}° angle. How far does base move?",
                "Two buildings {a} m and {b} m tall are {c} m apart. Find angle of elevation from shorter to taller.",
                "Ship travels {a} km at bearing {b}°, then {c} km at bearing {d}°. How far from start?",
            ]
        }
    },
    
    "number_theory": {
        "easy": {
            (1, 5): [
                # Odd/even
                "Is {a} odd or even?",
                "What is the next even number after {a}?",
                "What is the next odd number after {a}?",
                "Are {a} + {b} odd or even if both are even?",
                
                # Multiples
                "List the first {a} multiples of {b}.",
                "Is {a} a multiple of {b}?",
                "What is the {a}th multiple of {b}?",
                "Continue the multiples of {a}: {a}, {b}, {c}, ___",
            ],
            
            (6, 9): [
                # Factors
                "List all factors of {a}.",
                "What are the factors of {a}?",
                "How many factors does {a} have?",
                "Is {a} a factor of {b}?",
                
                # Prime numbers (recognition)
                "Is {a} a prime number?",
                "List all prime numbers less than {a}.",
                "What is the smallest prime number greater than {a}?",
                "How many prime numbers are there between {a} and {b}?",
                
                # Divisibility rules
                "Is {a} divisible by {b}?",
                "Which numbers divide evenly into {a}: {b}, {c}, {d}?",
                "Test divisibility: Is {a} divisible by 3?",
            ],
            
            (10, 12): [
                # Prime factorization
                "Find the prime factorization of {a}.",
                "Express {a} as a product of prime factors.",
                "What is {a} written as a product of primes?",
                
                # GCD (Greatest Common Divisor)
                "Find the GCD of {a} and {b}.",
                "What is the greatest common factor of {a} and {b}?",
                "Find GCD({a}, {b}, {c}).",
                
                # LCM (Least Common Multiple)
                "Find the LCM of {a} and {b}.",
                "What is the least common multiple of {a} and {b}?",
                "Find LCM({a}, {b}, {c}).",
            ]
        },
        
        "medium": {
            (1, 5): [
                # Patterns
                "Find the pattern: {a}, {b}, {c}, ___",
                "What rule generates: {a}, {b}, {c}, {d}?",
                "Continue: multiples of {a} that are also multiples of {b}.",
            ],
            
            (6, 9): [
                # Composite numbers
                "How many composite numbers are there between {a} and {b}?",
                "List all composite numbers from {a} to {b}.",
                "Is {a} prime or composite?",
                
                # Perfect numbers, squares, cubes
                "Is {a} a perfect square?",
                "What is the largest perfect square less than {a}?",
                "Is {a} a perfect cube?",
                "List all perfect squares between {a} and {b}.",
                
                # Modular arithmetic (basic)
                "What is {a} mod {b}?",
                "Find the remainder when {a} is divided by {b}.",
                "What is {a} ÷ {b}? Express with remainder.",
            ],
            
            (10, 12): [
                # Using GCD/LCM
                "Two gears have {a} and {b} teeth. After how many rotations do they align?",
                "Lights blink every {a} seconds and {b} seconds. When do they blink together?",
                "Bus A arrives every {a} minutes, Bus B every {b} minutes. When do they arrive together?",
                
                # Relatively prime (coprime)
                "Are {a} and {b} relatively prime (coprime)?",
                "Find all numbers less than {a} that are coprime to {a}.",
                "How many numbers less than {a} are relatively prime to {a}? (Euler's totient)",
                
                # Diophantine equations (basic)
                "Find integer solutions to {a}x + {b}y = {c}.",
                "Are there integer solutions to {a}x + {b}y = {c}?",
                
                # Congruences
                "Solve: {a}x ≡ {b} (mod {c})",
                "Find x where {a}x - {b} is divisible by {c}.",
            ]
        },
        
        "hard": {
            (6, 9): [
                # Advanced factorization
                "Express {a} as sum of two squares.",
                "Factor {a} using difference of squares.",
                "Find all divisors of {a}. How many are there?",
                
                # Number bases (introduction)
                "Convert {a} from base 10 to binary.",
                "Convert {a} from base 10 to base {b}.",
                "What is binary {a} in base 10?",
            ],
            
            (10, 12): [
                # Modular arithmetic
                "Calculate ({a} × {b}) mod {c}.",
                "Find {a}^{b} mod {c}.",
                "Simplify: ({a} + {b}) mod {c}.",
                
                # Chinese Remainder Theorem
                "Solve: x ≡ {a} (mod {b}) and x ≡ {c} (mod {d}).",
                "Find x where x mod {a} = {b} and x mod {c} = {d}.",
                
                # Fermat's Little Theorem
                "Use Fermat: Find {a}^{b} mod {c} where {c} is prime.",
                "If p = {a} is prime, what is {b}^({a}-1) mod {a}?",
                
                # Primes and factorization advanced
                "How many prime factors does {a} have (counting multiplicity)?",
                "Find the largest prime factor of {a}.",
                "Sum of divisors of {a}?",
                "How many divisors does {a}^{b} × {c}^{d} have?",
                
                # Sequences
                "Find the {a}th triangular number.",
                "What is the {a}th Fibonacci number?",
                "Calculate the {a}th term of sequence: {b}, {c}, {d}, ...",
                
                # Advanced problems
                "Prove {a} is irrational.",
                "Show that √{a} is irrational.",
                "Find rational approximation to √{a} using continued fractions.",
            ]
        }
    },
    
    "calculus": {
        "easy": {
            (10, 12): [
                # Limits (basic)
                "Find the limit: lim(x→{a}) {b}x + {c}",
                "Evaluate: lim(x→{a}) x²",
                "What is lim(x→{a}) {b}?",
                "Find: lim(x→{a}) (x + {b})",
                
                # Limits (substitution)
                "Find lim(x→{a}) (x² + {b}x + {c})",
                "Evaluate: lim(x→{a}) ({b}x² - {c})",
                
                # Slope of tangent (numerical)
                "Function f(x) = x². Estimate slope at x = {a} using points x = {a} and x = {b}.",
                "Average rate of change of f(x) = x² from x = {a} to x = {b}.",
            ]
        },
        
        "medium": {
            (10, 12): [
                # Derivatives (power rule)
                "Find the derivative: f(x) = x^{a}",
                "If f(x) = {a}x^{b}, find f'(x).",
                "Differentiate: y = {a}x^{b} + {c}x^{d}",
                "Find dy/dx: y = {a}x² + {b}x + {c}",
                
                # Derivatives (basic rules)
                "Find derivative: f(x) = {a}x^{b} - {c}x + {d}",
                "Differentiate: y = {a}/x",
                "Find f'(x) if f(x) = {a}x^{b} + {c}x^{d} + {e}",
                
                # Derivatives at a point
                "If f(x) = x², find f'({a}).",
                "Given f(x) = {a}x² + {b}x, find f'({c}).",
                "Find slope of tangent to y = x² at x = {a}.",
                
                # Integrals (basic power rule)
                "Find the antiderivative: ∫ x^{a} dx",
                "Evaluate: ∫ {a}x^{b} dx",
                "Find: ∫ ({a}x^{b} + {c}) dx",
                
                # Definite integrals (simple)
                "Evaluate: ∫[{a} to {b}] {c} dx",
                "Find: ∫[{a} to {b}] x dx",
                "Calculate: ∫[{a} to {b}] x² dx",
            ]
        },
        
        "hard": {
            (10, 12): [
                # Limits (indeterminate forms)
                "Find lim(x→{a}) (x² - {b})/(x - {c})",
                "Evaluate: lim(x→0) (sin(x))/x",
                "Find: lim(x→∞) ({a}x² + {b}x)/({c}x² + {d})",
                
                # Chain rule
                "Differentiate: f(x) = ({a}x + {b})^{c}",
                "Find f'(x): f(x) = ({a}x² + {b})^{c}",
                "Use chain rule: y = ({a}x + {b})^{c}",
                
                # Product and quotient rules
                "Differentiate: f(x) = ({a}x + {b})({c}x + {d})",
                "Find dy/dx: y = ({a}x²)/({b}x + {c})",
                "Use quotient rule: y = (x² + {a})/(x + {b})",
                
                # Implicit differentiation
                "Find dy/dx: x² + y² = {a}",
                "Differentiate implicitly: {a}x² + {b}y² = {c}",
                "Find dy/dx: xy = {a}",
                
                # Related rates
                "Radius increases at {a} cm/s. How fast is area changing when r = {b} cm?",
                "Ladder {a} m long slides down wall at {b} m/s. How fast is base moving when top is {c} m high?",
                
                # Optimization
                "Rectangle perimeter {a} cm. Find dimensions for maximum area.",
                "Maximize area of rectangle inscribed in semicircle radius {a}.",
                "Minimize surface area of cylinder volume {a} cm³.",
                
                # Integration techniques
                "Evaluate: ∫ {a}x({b}x² + {c})^{d} dx",
                "Find: ∫ ({a}x + {b})({c}x + {d}) dx",
                "Use substitution: ∫ {a}x(x² + {b})^{c} dx",
                
                # Area under curve
                "Find area between y = x² and x-axis from x = {a} to x = {b}.",
                "Calculate area: y = {a}x from x = {b} to x = {c}.",
                "Area between y = x² and y = {a}x.",
                
                # Applications
                "Velocity v(t) = {a}t + {b}. Find displacement from t = {c} to t = {d}.",
                "Acceleration a(t) = {a}. Initial velocity {b} m/s. Find velocity at t = {c}.",
                "Find average value of f(x) = {a}x² on [{b}, {c}].",
            ]
        }
    }
}
