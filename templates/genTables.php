<?php
	function createTableTemp($temp)
	{
		$sTable = '<table>';
		$sTable.= '<tr>';
		for($i; $i<120; $i++)
			if($i<$temp)
				$sTable.='<td style="background-color:#ffffff"></td>';
			else
				$sTable.='<td></td>';
		$sTable.= '</tr>'
		$sTable.= '</table>';
	}
?>