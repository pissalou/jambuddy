from abcutils import abc2beat


def test_abc2beat():
    assert abc2beat('a') == 1.0
    assert abc2beat('a1') == 1.0
    assert abc2beat('a/') == 0.5
    assert abc2beat('a/2') == 0.5
    assert abc2beat('a/4') == 0.25
    assert abc2beat('a//') == 0.25
    assert abc2beat('a3/4') == 0.75

    assert abc2beat('abc') == 3.0
    assert abc2beat('a,bc\'') == 3.0
    assert abc2beat('a1b2c3') == 6.0
    assert abc2beat('a/1b/2c/4') == 1.75
    assert abc2beat('ab/2c3/4') == 2.25
    assert abc2beat('ab/c//') == 1.75

    assert abc2beat('(ab) c') == 3.0
    assert abc2beat('a2b2 | c') == 5.0
    assert abc2beat('a2zz | c') == 5.0
