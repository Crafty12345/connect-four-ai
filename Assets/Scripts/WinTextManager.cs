using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class WinTextManager : MonoBehaviour
{

    public void SetWinText(SlotStatuses status,InstanceManager manager)
    {
        gameObject.SetActive(true);
        gameObject.GetComponent<TextMeshPro>().text = status.ToString() + " wins!";
        gameObject.GetComponent<TextMeshPro>().color = manager.colourData[status.ToString()];
    }

}
