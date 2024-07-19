import state
from abccoloramaview import AbcColoramaView


def test_start_position_2(capsys):
    with state.constant_bpm(120):
        abc = AbcColoramaView(["E/2", "E/2", "^F/2"], start_position=2, repeat=0)
        abc.run()
    assert capsys.readouterr().out != 'caca'
