import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__),os.pardir))
from utils.parsing import convert_ISO_date_to_string, convert_args_to_dict

def test_convert_ISO_date_to_string():
	assert convert_ISO_date_to_string("2019-01-01 00:00:00.000") == "January 01, 2019"
	assert convert_ISO_date_to_string("2018-01-01 00:00:00.000") == "January 01, 2018"
	assert convert_ISO_date_to_string("2019-12-01 00:00:00.000") == "December 01, 2019"
	assert convert_ISO_date_to_string("2019-01-31 00:00:00.000") == "January 31, 2019"

def test_convert_args_to_dict():
	arg = "type=adv something=yes yes=1"
	result = {"type":"adv", "something":"yes", "yes":"1"}
	assert convert_args_to_dict(arg) == result