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
            if (transform.parent.Find("restart_text").gameObject.activeInHierarchy && Input.GetKeyDown(KeyCode.Return))
            {
                transform.parent.Find("restart_text").gameObject.SetActive(false);
                instance.StartGame();
            }
        }
    }
}
