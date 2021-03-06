Learning by rote
################

`:sunglasses:`
==============

Calculus is full of formulae. As a mundane necessity of examination sometimes
those formulae must be committed to memory. I remember remembering
:maths:`-b\pm\frac{\sqrt{b^2-4ac}}{2a}`. On first sight, it looked huge! How
would I ever be able to reproduce something so arcane just *from memory*? After
I looked again, it didn’t seem so bad.

After a period, I had it down pat.

Because these were the GCSE days, when much learning seemed like repetition
“until it sinks in” without really understanding the significance of the thing,
we learned by rote. This was before the politics of *how* something was learned
would have struck any kind of chord with us; we just wanted to be outside.

It seems the time for learning by rote has come round again, this time with a
vengeance. Now I need to get down not one, not two, but twelve formulae
(granted, they are simple compared to the quadratic formula, but still). 

.. maths::

    \bgroup
    \def\arraystretch{2}
    \begin{tabular}{ | r | l | }
        \hline
        $f(x)$ & $f'(x)$ \\
        \hline
        $x^n$ & $nx^{n - 1}$ \\
        \hline
        $\sin x$ & $\cos x$ \\
        \hline
        $\cos x$ & $-\sin x$ \\
        \hline
        $\tan x$ & $\sec^2 x$ \\
        \hline
        $\sec x$ & $\sec x\tan x$ \\
        \hline
        $\mathrm{cosec} x$ & $-\mathrm{cosec} x \cot x$ \\
        \hline
        $\cot x$ & $-\mathrm{cosec}^2 x$ \\
        \hline
        $e^x$ & $e^x$ \\
        \hline
        $\ln x$ & $\frac{1}{x}$ \\
        \hline
        $\arcsin x$ & $\frac{1}{\sqrt{1 - x^2}}$ \\
        \hline
        $\arccos x$ & $-\frac{1}{\sqrt{1 - x^2}}$ \\
        \hline
        $\arctan x$ & $\frac{1}{1 + x^2}$ \\
        \hline
    \end{tabular}
    \egroup

How am I going to drum that lot into my head? I could print it out on a
pocket-sized sheet of paper and gaze lovingly at it when on the tube. Better
yet, I’m an adult now, so I could just get it tattooed to my wrist. But wait,
why not use the computer to do the drumming for me.

I want to be asked what the corresponding function is for a derivative and what
the derivative for a function is at regular intervals. Why don’t I just modify
my shell to ask me to give an answer before I am allowed to carry on.

Not being able to respond that the derivative of :maths:`\mathrm{cosec}x` is
:maths:`-\mathrm{cosec}x\cot x` within a few seconds would begin to burden my
productivity if I didn’t start learning ...

*Challenge accepted!*

The issue is that if I’m being asked the question in the terminal, then I’ll
have to cope with doing the translation of the LaTeX markup in my head. It
would be quite nice to display a little X window with a pretty, rendered SVG.

Unix philosophy to the rescue; there’s `a little binary`_ that comes with
ImageMagick that can do what we want.

.. _`a little binary`: http://www.imagemagick.org/script/display.php

The behaviour is going to be dead simple; when a new shell is invoked, open a
window showing a random SVG of some :maths:`f(x)`, wait for the window to be
closed, wait for some LaTeX input, check aforementioned input against the
expected value. If the answer is correct, exit. If the answer is wrong then
show the correct answer along with the question :maths:`f(x) = f'(x)`, wait for
the window to be closed, exit.

The first job we have is to put together a table of questions, answers in LaTeX
markup and render SVGs for the questions :maths:`f(x)` and the questions with
their answers :maths:`f(x) = f'(x)`.

====================  =============================
``f(x)``              ``f'(x)``
====================  =============================
``x^n``               ``nx^{n - 1}``
``\sin x``            ``\cos x``
``\cos x``            ``-\sin x``
``\tan x``            ``\sec^2 x``
``\sec x``            ``\sec x\tan x``
``\mathrm{cosec} x``  ``-\mathrm{cosec} x \cot x``
``\cot x``            ``-\mathrm{cosec}^2 x``
``e^x``               ``e^x``
``\ln x``             ``\frac{1}{x}``
``\arcsin x``         ``\frac{1}{\sqrt{1 - x^2}}``
``\arccos x``         ``-\frac{1}{\sqrt{1 - x^2}}``
``\arctan x``         ``\frac{1}{1 + x^2}``
====================  =============================

Luckily, I’ve got `some code`_ hanging about that will take a LaTeX string like
we have above and return an SVG string with the notation I need to be able to
recognise. I just need to loop through the table above spitting out SVG files
for questions :maths:`f(x)` and questions with their answers :maths:`f(x) =
f'(x)`.

.. _`some code`: https://github.com/bmcorser/bade/blob/master/bade/directives/eqtexsvg.py

Because I don’t really want to write out a file called ``\frac{1}{1 + x^2}``,
I’m just going to make a short hash of the LaTeX string and use that as the
file name. I can use the same idea to check the veracity of the answer provided.

So, let’s represent the above as a mapping in Python, and render the SVGs we
need:

.. code-block:: python

    from bade.directives.eqtexsvg import eqtexsvg
    import hashlib

    fx_fdx = {
        'x^n':               'nx^{n - 1}',
        '\\sin x':           '\\cos x',
        '\\cos x':           '-\\sin x',
        '\\tan x':           '\\sec^2 x',
        '\\sec x':           '\\sec x\\tan x',
        '\\mathrm{cosec} x': '-\\mathrm{cosec} x \\cot x',
        '\\cot x':           '-\\mathrm{cosec}^2 x',
        'e^x':               'e^x',
        '\\ln x':            '\\frac{1}{x}',
        '\\arcsin x':        '\\frac{1}{\\sqrt{1 - x^2}}',
        '\\arccos x':        '-\\frac{1}{\sqrt{1 - x^2}}',
        '\\arctan x':        '\\frac{1}{1 + x^2}',
    }

    hashes = {}

    for fx, fdx in fx_fdx.items():
        # write f(x) to file
        fx_hash = 'q-' + hashlib.sha1(fx.encode('utf8')).hexdigest()[:7]
        fx_svg = eqtexsvg("\\( {0} \\)".format(fx), inline=False)
        with open(fx_hash, 'w') as fx_fh:
            fx_fh.write(fx_svg)

        # write f(x) = f'(x) to file
        fdx_hash = hashlib.sha1(fdx.encode('utf8')).hexdigest()[:7]
        fdx_svg = eqtexsvg("${0} = {1}$".format(fx, fdx), inline=False)
        with open(fdx_hash, 'w') as fdx_fh:
            fdx_fh.write(fdx_svg)

        # remember association of hashes
        hashes[fx_hash] = fdx_hash

    for fx_hash, fdx_hash in hashes.items():
        print("{0} {1}".format(fx_hash, fdx_hash))

Easy-peasy. A bunch of files just got written to `the directory`_ we ran `the
script`_ in and the script printed a pretty map that tells us about the
associations between the files that were written:

.. _`the directory`: https://github.com/bmcorser/_bmcorser.github.io/tree/master/blog/2015/12/01
.. _`the script`: https://github.com/bmcorser/_bmcorser.github.io/blob/master/blog/2015/12/01/fx_fdx.py

.. code-block:: bash

    q-189199f c65ec7a
    q-5600f00 d849a01
    q-67fd40d 5600f00
    q-a297bb9 b82f717
    q-43630ee 61d8e53
    q-26d1990 566261d
    q-1624dce 1624dce
    q-bd04e97 d261fd4
    q-d6d9338 5edd4ce
    q-0741fac e9e9dc6
    q-4f1ae87 2ba2cbb
    q-3ad999b d339226

The ``q-`` prefix is to cover the case where an answer is the same as the
question (ie. :maths:`\sin x \rightarrow \cos x \rightarrow -\sin x`).

Now to write the program to flash these images and check answers. Because this
is going to frequently interrupt me whilst I am doing things, it needs to be
pretty snappy if it’s not going to be get on my nerves. So, let’s write it in
Rust. We can do that by mostly copy‘n’pasting code from documentation.

Let’s represent our above associations between question and answer with a
``std::collections::HashMap``, almost as nice as writing a literal `:wink:`

.. code-block:: rust

    let mut fx_fdx = HashMap::new();

    fx_fdx.insert("q-0741fac", "e9e9dc6");
    // ...
    fx_fdx.insert("q-d6d9338", "5edd4ce");

We also need to randomly select from the above, there’s code in the crate
`docs`_ for doing that, and we can has a destructuring assignment like Python
and ES6:

.. _`docs`: https://doc.rust-lang.org/rand/rand/fn.sample.html

.. code-block:: rust

    extern crate rand;
    use rand::{thread_rng, sample};

    let mut rng = thread_rng();
    let (fx, fdx) = sample(&mut rng, fx_fdx, 1).pop().unwrap();

Next we need to flash images using ``display``, for which we use
``std::process::Command`` in Rust. We’ll need to do this for both questions and
answers, so let’s write a function taking a file name:

.. code-block:: rust

    fn display (name: &str) {
        Command::new("display")
            .arg("-border").arg("10")
            .arg("-bordercolor").arg("white")
            .arg(name)
            .output()
            .unwrap_or_else(|e| { panic!("{}", e) });
    }

This function doesn’t actually need to return anything, since we just halt
execution whilst the user (me) looks at the image being flashed up. Again,
getting input from the user is just `:spaghetti:` from the docs. I won’t reproduce
it here. Once we have the answer provided, we need to hash it and compare the
obtained hash with the expected hash. Another tiny function, writ large:

.. code-block:: rust

    extern crate sha1;
    use sha1::Sha1;

    fn compare (input: String, fdx: &str) -> bool {
        let mut input_sha1 = Sha1::new();
        input_sha1.update(input.as_bytes());
        fdx.as_bytes() == input_sha1.hexdigest()[..7].as_bytes()
    }

This is where my Rust gets a little hazy. Should I cast both things to bytes
here? I don’t know, please feel free to `PR against this post`_ if there’s a
suggestion!

.. _`PR against this post`: https://github.com/bmcorser/_bmcorser.github.io/edit/master/blog/2015/12/01/learning-by-rote.rst

Now we have everything we need and just need to write the logic combining our
``compare`` and ``display`` functiongs for showing the answer (in case of an
incorrect answer) or just exiting:

.. code-block:: rust

    match compare(input, fdx) {
        true => {},
        false => display(fdx)
    };

Look `on GitHub`_ to see the whole thing put together. I simply add a line to
my ``~/.zshrc`` to execute the binary every time a new shell boots up and
there we have it, auto-revision!


.. figure:: /assets/images/learning-by-rote.gif
            :class: full

.. _`on GitHub`: https://github.com/bmcorser/_bmcorser.github.io/blob/master/blog/2015/12/01/fx_fdx/src/main.rs
