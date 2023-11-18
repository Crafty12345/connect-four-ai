using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MoveData
{
    public SlotStatuses player;
    public bool win;

    public MoveData(SlotStatuses player, bool win)
    {
        this.player = player;
        this.win = win;
    }

}
