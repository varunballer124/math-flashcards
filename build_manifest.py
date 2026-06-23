#!/usr/bin/env python3
"""Build the unified flashcard manifest (cards.json) from the 3 extracted decks.

For every card we keep the full worked-card image (the "answer") and generate a
title-strip crop (the "front" recall cue). Sections are assigned by id-range
(read off the source PDFs). Titles are best-effort labels used for search; the
displayed front is always the cropped strip, so a label typo never shows.
"""
import json, os
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
FRONT_FRAC = 0.135   # top slice of each card = "Section | Topic" banner

# ── section boundaries (local card id ranges within each part) ───────────────
SECTIONS = {
    1: [
        ("Essential Quant Skills", 1, 58),
        ("Linear & Quadratic Equations", 59, 88),
        ("Properties of Numbers", 89, 152),
        ("Roots & Exponents", 153, 164),
    ],
    2: [
        ("Roots & Exponents", 1, 46),
        ("Inequalities & Absolute Values", 47, 68),
        ("General Word Problems", 69, 100),
        ("Unit Conversions", 101, 105),
        ("Rate Problems", 106, 130),
        ("Work Problems", 131, 147),
        ("Ratios", 148, 164),
    ],
    3: [
        ("Percent Word Problems", 1, 12),
        ("Overlapping Sets", 13, 21),
        ("Statistics", 22, 46),
        ("Combinations & Permutations", 47, 82),
        ("Probability", 83, 102),
        ("Coordinate Geometry", 103, 126),
        ("Functions & Sequences", 127, 158),
    ],
}

# ── best-effort topic titles (search labels only) ────────────────────────────
TITLES = {1: {}, 2: {}, 3: {}}
TITLES[1] = {
1:"Connecting a Percent to a Decimal",2:"Estimation With Multiplication and Division",
3:"Using the Units Digit of a Number to Solve Problems Efficiently",4:"Comparing Negative Fractions",
5:"PEMDAS: The Order of Mathematical Operations",6:"The Order of Operations in Fractions",
7:"Time-Saving Properties of Addition",8:"Time-Saving Properties of Multiplication",
9:"The Distributive Property",10:"The Distributive Property Allows Us to Factor Out Common Factors",
11:"Simplifying Addition by Rewriting Numbers",12:"Introduction to Factorials",13:"Factoring Factorials",
14:"Converting a Decimal to a Percent",15:"Simple Fractions: Proper and Improper Fractions",
16:"The Least Common Denominator",17:"Equivalent Fractions",
18:"Adding and Subtracting Fractions with the Same Denominator",19:"Adding Fractions with Unlike Denominators",
20:"Adding a Whole Number and a Fraction",21:"Subtracting a Fraction from a Whole Number",
22:"Multiplying and Dividing Fractions: Part 1",23:"Multiplying and Dividing a Whole Number by a Fraction",
24:"Simplify Fractions Before Multiplying: Top-and-Bottom Simplification",25:"Reciprocals and “1 Over a Fraction”",
26:"Simplifying Complex Fractions: Technique #1",27:"Using a Reference Point to Compare the Size of Fractions",
28:"Comparing the Size of Fractions Using the Bowtie Method",29:"Comparing Fractions by Using a Common Denominator",
30:"Comparing Fractions by Using a Common Numerator",31:"Decimals",32:"Adding and Subtracting Decimals",
33:"Multiplying Decimals",34:"Dividing Decimals",35:"Rounding Down Positive Integers",36:"Arranging Decimals by Size",
37:"Converting a Percent to a Fraction",38:"Converting a Fraction to a Percent",
39:"Converting a Fraction to a Decimal When the Denominator is NOT a Power of 10",
40:"Converting a Terminating Decimal to a Fraction",41:"Base Fractions and Their Decimal and Percent Equivalents",
42:"Squaring and Taking the Square Root of a Number Between 0 and 1",43:"Properties of Square Roots: Squaring a Square Root",
44:"Properties of Square Roots: Splitting a Single Root into a Product",45:"Simplify Fractions Before Multiplying: Cross Simplification",
46:"Rounding Up Positive Integers",47:"Multiplying and Dividing Fractions: Part 2",
48:"Perfect Squares Have a Finite Number of Units Digits",49:"Converting an Improper Fraction to a Mixed Number",
50:"Simplifying Subtraction by Rewriting Numbers",51:"Estimation With Addition and Subtraction",
52:"Simplifying Complex Fractions: Technique #2",53:"Simplifying Factorial Expressions",
54:"Subtracting Fractions with Unlike Denominators",55:"Converting a Mixed Number to an Improper Fraction",
56:"Rounding Decimals Down to a Certain Place Value",57:"Rounding Decimals Up to a Certain Place Value",
58:"Rounding Up Numbers When the Original Digit is 9",59:"Solving an Equation for One Variable",
60:"Solving for an Expression",61:"Solving a System for Two Variables: Substitution Method",
62:"Solving a System for Two Variables: Combination with Subtraction",
63:"Solving a System for Two Variables: Combination with Addition",
64:"Combining Equations When the Coefficients are Different",
65:"Determining the Number of Solutions to a System of Linear Equations",66:"Equations with Fractions",
67:"Solving for One Variable in Terms of Other Variables",68:"Factoring Out Common Factors",
69:"The Zero Product Property",70:"Factoring Quadratic Equations",71:"Foiling Quadratic Equations",
72:"Three Common Quadratic Identities",73:"The Difference of Squares",74:"Differences of Squares with Roots",
75:"Advanced “FOIL” Techniques",76:"Another Way to Express Negative One",
77:"Constant Terms and Coefficients in Quadratic Equations",78:"Quadratic Equations That Result From Removing Fractions",
79:"The Quadratic Formula",80:"Determining the Number of Roots of a Quadratic Equation",
81:"Vieta’s Formulas for the Roots of a Quadratic Equation",82:"Hidden Quadratic Equations",
83:"Equation Trap: An Equation Has 2 or More Solutions",84:"Assuming the Value of a Variable Cannot Be Zero",
85:"Squared Algebraic Expressions",86:"Implied Differences of Squares",
87:"Using Difference of Squares to Simplify Large Expressions",
88:"When One Equation Determines Unique Values for Two Variables",89:"Factorial Notation",
90:"Remainders After Division by 5",91:"Two Consecutive Integers Never Share the Same Prime Factors",
92:"Properties of Zero",93:"Properties of One",
94:"Unique Prime Factors Don’t Change When a Number is Raised to a Power",95:"A Second Approach to Finding the GCF",
96:"The LCM Provides All Unique Prime Factors of a Set of Integers",
97:"If x is Divisible by Two Numbers, x is Divisible by Their LCM",98:"Addition and Subtraction Rules for Even Numbers",
99:"Multiplication Rules for Even and Odd Numbers",100:"Division Rules for Even and Odd Numbers",
101:"Test for Even and Odd Algebraic Expressions",102:"Even/Odd Exponents Versus Positive/Negative Answers",
103:"Factors",104:"Multiples",105:"Prime Numbers",106:"Finding the Number of Prime Factors of a Number",
107:"Finding the Number of Odd Positive Factors of a Number",108:"Number of Prime Factors vs. Unique Prime Factors",
109:"Prime Factorization When the Exponents are Variables",110:"The Least Common Multiple (LCM)",
111:"A Second Approach to Finding the LCM",112:"The Greatest Common Factor (GCF)",
113:"LCM and GCF When One Number Divides Evenly Into the Other",
114:"Knowing LCM and GCF Gives the Product of Two Integers",115:"Using the LCM to Solve Repeating-Pattern Questions",
116:"For Divisibility, Think About Prime Factorization",117:"Factors of Factors",118:"Evaluating Divisibility Expressions",
119:"Divisibility Rules: Part 1",120:"The Product of n Consecutive Integers is Divisible by n!",
121:"The Product of Consecutive Integers in Algebraic Expressions",122:"Product of Consecutive Even Integers",
123:"A Formula for Division",124:"The Range of Possible Remainders",125:"Listing Possible Values of the Dividend",
126:"Combining Remainder Information",127:"Converting a Remainder From Decimal Form to Fraction Form",
128:"Multiplying Remainders",129:"Adding and Subtracting Remainders",130:"Determining the Number of Trailing Zeros",
131:"Using Trailing Zeros to Determine the Number of Digits",132:"Determining the Number of Leading Zeros in a Decimal",
133:"Division Properties of Factorials",134:"Number of Primes in a Factorial (Shortcut)",
135:"Number of Primes in a Factorial: Non-Prime Divisor Base",136:"Number of Primes in a Factorial: Prime-Power Divisor Base",
137:"Prime Factorization of a Perfect Square Has Only Even Exponents",
138:"Prime Factorization of a Perfect Cube: Exponents are Multiples of 3",139:"Terminating Decimals",
140:"Remainders Exhibit Patterns",141:"Remainder Patterns in Powers",142:"Units Digits that Have No Change",
143:"Remainders After Division by 10^n",144:"Addition and Subtraction Rules for Odd Numbers",
145:"Divisibility Rules: Part 2",146:"Division Rules for Even and Odd Numbers",
147:"Units Digits that Have a Pattern of Four",148:"Units Digits that Have a Pattern of Two",
149:"Divisibility Rules: Part 3",150:"Units Digits that Have a Pattern of One",
151:"Divisibility Rules: Part 4",152:"Divisibility Rules: Part 5",
153:"Power to a Power to a Power Rule",154:"Number Properties of Exponents and Roots for Numbers > 1",
155:"Estimating with Exponents",156:"Powers of Ten",157:"Scientific Notation",
158:"Multiplication and Division with Scientific Notation",159:"Square Roots of Large Perfect Squares",
160:"Roots of Small Perfect Squares",161:"Squaring Decimals with Zeros",162:"The Square Root Symbol",
163:"Even-Indexed Roots",164:"Perfect Squares",
}
TITLES[2] = {
1:"The Cube Root",2:"Multiplying Radicals",3:"Simplifying Radicals",4:"Dividing Radicals",
5:"Multiply/Divide Non-Radicals by Non-Radicals and Radicals by Radicals",6:"Approximating Square Roots",
7:"Approximating Other Roots",8:"Addition and Subtraction of Radicals",9:"Add and Subtract Only Like Radicals",
10:"Rationalization: Single-Term Radical in the Denominator",11:"Rationalization: Binomial Denominator with a Radical",
12:"Taking the Nth Root of an Expression or an Equation",13:"Be Careful Taking the Square Root of a Squared Binomial",
14:"Solving Equations with Square Roots",15:"If the Bases are Equal, the Exponents May be Equal",
16:"Multiplication of Exponential Expressions with the Same Base",17:"Division of Exponential Expressions with the Same Base",
18:"The Power to a Power Rule",19:"If the Bases Are Not the Same, Make Them the Same",
20:"Multiplication of Exponentials with Different Bases and Like Exponents",
21:"Division of Different Bases and Like Exponents",22:"Distributing an Exponent over Multiple Factors",
23:"Prime Factorization with Exponents",24:"Prime Factorization Simplifies Fractional Exponential Expressions",
25:"Radicals Can Be Expressed in Exponential Form",26:"Nested Roots",27:"Removing the Radical and the Exponent",
28:"Comparing Roots",29:"Be Careful When Squaring a Binomial",30:"Raising a Base to a Negative Exponent",
31:"Quadratic Expressions as Exponents",32:"Any Nonzero Base Raised to the Zero Power Equals One",
33:"Any Base Raised to the 1st Power is that Base",34:"Addition/Subtraction of Like Bases or Like Radicals",
35:"A Special Trick When Adding Like Bases with Equal Exponents",36:"Adding and Subtracting Fractions that Contain Exponents",
37:"Comparing Fractions with Exponents",38:"Multiplying Radicals with Different Indices",
39:"Number Properties of Exponents and Roots for Numbers < -1",40:"The Square Root of a Squared Entity",
41:"Odd-Indexed Roots",42:"Roots of Large Perfect Powers",43:"Square Roots of Small Perfect Squares",
44:"Comparing Exponents",45:"Number Properties of Exponents/Roots for Numbers Between 0 and 1",
46:"Number Properties of Exponents/Roots for Numbers Between 0 and -1",47:"The Real Number Line",
48:"Absolute Value",49:"Solving Equations with Absolute Values",50:"When Two Absolute Values Are Equal",
51:"Inequalities with Absolute Values",52:"Beware of Inequalities with Multiple Unknown Variables",
53:"Simplifying Inequalities with x squared",54:"Checking Solutions in Absolute-Value Equations",
55:"The Minimum or Maximum Value of a Product",56:"Moving from Solving Equations to Solving Inequalities",
57:"Multiplying or Dividing an Inequality by a Negative Number",58:"Systems of Inequalities",
59:"The Compound Inequality",60:"Working with Inequalities and Equations",
61:"Substituting from an Equation into a Compound Inequality",
62:"Multiplying/Dividing Compound Inequalities by a Positive Number",63:"The Basics of Inequalities (≥ and ≤)",
64:"Adding and Subtracting with Compound Inequalities",65:"Adding and Subtracting Compound Inequalities",
66:"Multiplying/Dividing Compound Inequalities by a Negative Number",67:"Graphing > and ≥ Inequalities on the Number Line",
68:"Graphing < and ≤ Inequalities on the Number Line",69:"Age Problems",70:"Length Problems",
71:"Weight Problems",72:"Money Problems",73:"Coin Problems",74:"Word Problems with Variables in the Answer Choices – Part 1",
75:"Moving From Words to Equations",76:"Price Per Item",77:"Word Problems with Differing Unit Prices and Quantities",
78:"Profit and Loss Problems",79:"Splitting the Cost",80:"Which Salary Should I Choose? How Much Will I Make?",
81:"Which Price Structure Makes the Most Sense?",82:"The Equalization of Rates",83:"Fraction Word Problems",
84:"The Fractional Parts of a Whole Must Sum to the Whole",85:"Simple Interest Problems",86:"Compound Interest Problems",
87:"The Linear Growth Formula",88:"Making a Growth Table to Solve Linear Growth Problems",89:"Exponential Growth Problems",
90:"Exponential Decay Problems",91:"Digit Problems",92:"Consecutive Integer Word Problems",
93:"Consecutive Even or Odd Integers",94:"Consecutive Multiples of Integers",95:"Dry Mixtures",96:"Wet Mixtures",
97:"Mixtures with Replacement",98:"Word Problems with Inequalities",99:"Objects in a Line – One Named Object",
100:"Word Problems with Variables in the Answer Choices – Part 2",101:"The Unit Conversion Process",
102:"Conversions Involving Two Sets of Units",103:"Using Two Steps to Convert One Measurement",
104:"Unit Conversions Involving Variables",105:"Unit Conversions Involving Squared and Cubed Units",
106:"When a Given Measurement is an Inequality",107:"The Matrix Approach to Rate-Time-Distance Problems",
108:"Variation 2: Two Objects Leave at Different Times",109:"Variation 3: One Object Faster than Another",
110:"Variation 4: One Object Relatively Faster than Another",111:"The Rate-Time-Distance Formula",
112:"Average Rate Questions",113:"Finding the Average Rate When Distances Are Unknown – Variable Method",
114:"Converging Rate Questions",115:"Diverging Rate Questions",116:"Round-Trip Rate Questions",
117:"Catch-Up Rate Questions",118:"Catch-Up and Pass Rate Questions – Part 1",119:"Catch-Up and Wait Rate Questions",
120:"Relative Motion Rate Questions",121:"If/Then Rate Questions",122:"Beware Time-Zone Changes in Rate-Time-Distance Problems",
123:"Fuel Efficiency – Another Rate",124:"DS Rate Questions with Inequalities: 9-Step Strategy – Part 1",
125:"Elementary Rate Questions with Variables in the Answer Choices",126:"Solving Average Rate Problems When the Average Rate is Known",
127:"Matrix Approach to Rate-Time-Distance: Make Sure Units Are Compatible",128:"DS Rate Questions with Inequalities: 9-Step Strategy – Part 2",
129:"Catch-Up and Pass Rate Questions – Part 2",130:"Finding the Average Rate When Distances Are Unknown – Numerical Method",
131:"The Rate-Time-Work Formula",132:"Determining an Object’s Work Rate",133:"The Matrix Approach to Solving Work Problems",
134:"Single Worker Problems",135:"Single Worker Problems with Variables in the Answer Choices",136:"Combined Worker Problems",
137:"Two Objects Work Together For the Same Amount of Time",138:"Two Objects Begin Together, but One Stops Before Completion",
139:"Two Objects Work Together, But One Has an Unknown Time",140:"Percent of a Job Done and Fraction of a Job Done",
141:"Combining Rates",142:"Determining a Combined Rate From Three or More Combined Rates",143:"Opposing Worker Problems",
144:"Matrix Approach to Work Problems (Continued)",145:"One Worker Faster/Slower by a Percent or Fraction – Part 1",
146:"One Worker Faster/Slower by a Percent or Fraction – Part 2",147:"Fractional Workers Problems",
148:"More Complicated Inverse Variation",149:"The Information that All Ratios Express",150:"A Ratio Alone Does Not Provide Actual Quantities",
151:"The Ratio Multiplier",152:"Determining the Ratio Multiplier",153:"Understanding What Constitutes a Useful Ratio",
154:"Using Like Variables in Ratios",155:"The Multipart Ratio and the Least Common Multiple (LCM)",
156:"Adjusting Ratios with Multiplication and Division",157:"Proportions",158:"Direct Variation",159:"Inverse Variation",
160:"Combined Variation",161:"Ratios Can Be Written in Three Common Equivalent Forms",162:"Adding/Subtracting to Achieve a Desired Ratio",
163:"More Complicated Direct Variation",164:"Joint Variation",
}
TITLES[3] = {
1:"Percent Profit",2:"“Percent of” Problems",3:"“What Percent” Problems",4:"“Percent Less Than” Problems",
5:"“Percent Greater Than” Problems",6:"Increasing or Decreasing a Value by a Variable Percent",7:"Sales Tax Problems",
8:"Successive Percent Changes",9:"“Percent Change” Problems",10:"Imbalances in Percent Changes – Part 1",
11:"Using a Variable or Picking 100",12:"Imbalances in Percent Changes – Part 2",13:"Converting Data for a Set-Matrix Approach",
14:"The Blueprint of the Set-Matrix – Part 1",15:"Three Overlapping Sets",16:"Percents in Overlapping Sets Problems",
17:"Fractions in Overlapping Sets Problems",18:"Integrating Algebra Into Overlapping Sets Problems",
19:"Solving for a Combination of Cells in an Overlapping Sets Problem",20:"Number Of Members in Either Set",
21:"The Blueprint of the Set-Matrix – Part 2",22:"Weighted Averages with Percents",23:"The Median of a Set With an Odd Number of Terms",
24:"The Median of a Set With an Even Number of Terms",25:"Alternative Median Strategy: Sets With an Odd Number of Terms",
26:"Adding a Number That is Equal to the Mean: Effect on Standard Deviation",27:"Average (Arithmetic Mean)",
28:"When the Mean is Equal to the Median",29:"Mode",30:"Range",31:"The Minimum Possible Range When the Sets are Combined",
32:"Finding an Unknown Term in a Set When the Average is Known",33:"Calculating Sums When We Don’t Know the Individual Data Points",
34:"How the Weightings Affect the Weighted Average",35:"Units of Standard Deviation",
36:"Adding or Subtracting the Same Value to/from All Terms: Effect on Standard Deviation",
37:"Multiplying or Dividing a Data Set by the Same Factor: Effect on Standard Deviation",
38:"Alternative Median Strategy: Sets With an Even Number of Terms",39:"The Maximum Possible Range When the Sets are Combined",
40:"When the Standard Deviation of a Set is Zero",41:"Counting Consecutive Evens and Odds, Inclusive of the First and Last Numbers",
42:"Counting Consecutive Multiples, Inclusive of the First and Last Numbers in a Set",43:"Determining the Average of an Evenly Spaced Set",
44:"Counting the Multiples of Integer A or B in a Set of Consecutive Integers",
45:"Counting the Multiples of Integer A or B, But Not of Both, in a Set of Consecutive Integers",46:"Weighted Average",
47:"Recognizing Combination Problems",48:"Solving Combination Problems – The Combination Formula",
49:"Counting Triangles when in Three Available Points are Collinear",50:"Counting Triangles when Three or More Available Points are Collinear",
51:"Handshake Questions",52:"Equivalent Property of Combinations",53:"The Fundamental Counting Principle",
54:"Choosing Multiple Items from Multiple Groups Using the Word “Or”",55:"Choosing “At Least” Some Number of Items",
56:"Combinations with Restrictions: Some Items Must Be Chosen",57:"Combinations with Restrictions: Some Items Must Not Be Chosen",
58:"Some Number of Items in a Set Must Be Chosen and Another Number of Items Cannot Be Chosen",59:"Collectively Exhaustive Events",
60:"Some Items can never be together in the same subgroup",61:"The Special Case of Choosing at Least 1 Item from a Group",
62:"Calculating an Unknown Number of Items in a Group in a Combination",63:"Permutations",64:"Recognizing Permutations",
65:"Solving Permutation Problems – The Permutation Formula",66:"The Permutation Formula for Indistinguishable Items",
67:"Counting 2-Dimensional Paths When There Are Checkpoints Between the Start and End Points",68:"Circular Arrangements",
69:"Arrangements with Restrictions",70:"Using the Anchor Method to Solve Arrangements with Restrictions",
71:"When Some Items Must be Together: Link Those Items Together",72:"Some Items Can’t be Next to Each Other",
73:"Calculating an Unknown Number of Items in a Group in a Permutation",74:"Solving for Unknowns Using the Equivalent Property of Combinations",
75:"Multi-Digit Problems with Restrictions",76:"Creating Codes",77:"Starting with the Most Restrictive Choice in a Multi-Digit Problem",
78:"Dependent Combinations",79:"Counting 3-Dimensional Paths",80:"Solving Combination Problems – The Box-and-Fill Method",
81:"Solving Permutation Problems – The Box-and-Fill Method",82:"Some Items Must Be Chosen and Another Number Cannot Be Chosen",
83:"The Probability of Creating Codes",84:"Sample Spaces",85:"Complementary Events",86:"The Probability of A and B – Independent Events",
87:"The Probability of A and B – Dependent Events",88:"The Addition Rule Concerning Mutually Exclusive Events",
89:"The Basic Probability Formula",90:"Accounting for Multiple Outcomes",91:"“At Least” Probability Problems",
92:"The Special Case Of “At Least 1” Probability Problems",93:"Blending Combinatorics and Probability",
94:"The Probability That Some Number of Items Must Be Selected",95:"The Probability That Some Number of Items Must Not Be Selected",
96:"The Probability That Some Number of Items Must Be Selected While Other Items Must Not Be Selected",
97:"The Probability of At Least Some Number of Events Occurring",98:"Quadratics and Probability",99:"Algebra and Probability",
100:"Probability with Permutations",101:"Probability of Two Non-Mutually Exclusive Events",
102:"The Addition Rule Concerning Events That Are Not Mutually Exclusive",103:"The Midpoint Formula",
104:"Points on the Coordinate Plane",105:"The Four Quadrants of the Coordinate Plane",106:"Graphing Lines on the Coordinate Plane",
107:"Slope of a Line",108:"The Slope of a Line Can Be Positive, Negative, Zero, or Undefined",109:"Lines with Positive Slopes",
110:"Lines with Negative Slopes",111:"Lines with Zero Slope (Horizontal Lines)",112:"Lines with Undefined Slope (Vertical Lines)",
113:"The Slope of the Line and Steepness of the Line",114:"The Slope-Intercept Equation",115:"Graphing Lines Using the Slope-Intercept Equation",
116:"Working with the Slope-Intercept Equation",117:"Equations For Horizontal and Vertical Lines",118:"The Standard Form of the Equation of a Line",
119:"The Information Needed To Define A Line",120:"Using a Right Triangle to Calculate the Length of a Line Segment",
121:"The Coordinate Plane",122:"Parallel Lines",123:"Perpendicular Lines",124:"Distance Between Two Points",
125:"Determining the Equation of a Line from Two Points on the Line",126:"Determining the Point of Intersection of Two Lines",
127:"Introduction to Functions",128:"The Domain of a Function",129:"The Range of a Function (1)",130:"The Range of a Function (2)",
131:"Using Minimum and Maximum Values to Determine the Range of a Function",132:"Compound Functions",133:"Graphs of Functions",
134:"Maximum and Minimum Values of a Quadratic Function",135:"Word Problems with Maximum and Minimum Values of a Quadratic Function",
136:"From f(x) to Everything",137:"Symbolism Questions",138:"Text-based Definitions in Symbolism Questions",
139:"Solving Equations in Symbolism Questions",140:"Symbolism Questions with Two or More Variables or Symbols",
141:"Answering Questions about an Algorithm’s Net Effect",142:"Word Problems Involving Functions",
143:"Testing Properties of Functions by Testing Numbers",144:"Functions and Properties of Numbers",145:"Sequences",
146:"Recursive Notation",147:"Arithmetic Sequences",148:"Sum of the Terms of an Arithmetic Sequence",149:"Equally Spaced Tick Marks",
150:"Tick Mark Questions When We Are Not Given Consecutive Values",151:"Equally Spaced Number Lines with Exponents",
152:"Geometric Sequences",153:"Repeating Sequences",154:"Finding Terms in Repeating Sequences",155:"Finding Sums in Repeating Sequences",
156:"Cancelling Terms in a Sequence: Finding the Sum of a Set of Consecutive Terms",
157:"Cancelling Terms in a Sequence: Finding the Product of a Set of Consecutive Terms",
158:"Cancelling Terms in a Sequence (Continued)",
}


def section_for(part, lid):
    for name, lo, hi in SECTIONS[part]:
        if lo <= lid <= hi:
            return name
    return "Other"


def main():
    cards = []
    gid = 0
    for part in (1, 2, 3):
        adir = os.path.join(ROOT, "assets", f"part{part}")
        man = json.load(open(os.path.join(adir, "manifest.json")))
        fdir = os.path.join(adir, "front")
        os.makedirs(fdir, exist_ok=True)
        for m in man:
            gid += 1
            lid = m["id"]
            full = m["file"]
            # build the front title-strip crop
            im = Image.open(os.path.join(adir, full)).convert("RGB")
            w, h = im.size
            strip = im.crop((0, 0, w, int(h * FRONT_FRAC)))
            fname = f"front_{lid:03d}.jpg"
            strip.save(os.path.join(fdir, fname), quality=88)
            cards.append({
                "gid": gid,
                "part": part,
                "lid": lid,
                "section": section_for(part, lid),
                "title": TITLES[part].get(lid, ""),
                "full": f"assets/part{part}/{full}",
                "front": f"assets/part{part}/front/{fname}",
            })
    out = {"count": len(cards), "cards": cards,
           "sections": sorted({c["section"] for c in cards})}
    json.dump(out, open(os.path.join(ROOT, "cards.json"), "w"), indent=1)
    print(f"wrote cards.json with {len(cards)} cards across {len(out['sections'])} sections")
    from collections import Counter
    c = Counter(c["section"] for c in cards)
    for s in out["sections"]:
        print(f"  {c[s]:>4}  {s}")


if __name__ == "__main__":
    main()
