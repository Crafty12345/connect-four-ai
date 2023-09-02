using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;

public class PlayerManager : MonoBehaviour
{
    public InstanceManager instance;

    public void DoEnable(InstanceManager _instance)
    {
        instance = _instance;
    }

    // Update is called once per frame
    void Update()
    {
        if (gameObject.activeSelf)
        {
            if (Input.anyKeyDown && !instance.turn_played && !instance.gameFinished)
            {
                instance.PlayerPlayTurn();
            }
            else if (Input.anyKeyDown && instance.gameFinished && Input.GetKeyDown(KeyCode.Return))
            {
                transform.parent.Find("restart_text").gameObject.SetActive(false);
                instance.StartGame();
            }
        }
    }
}
