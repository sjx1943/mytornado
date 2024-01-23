function showResult() {
  const amountInput = document.getElementById('amount');
  const unitTypeSelect = document.getElementById('unit-type');
  const resultDiv = document.getElementById('result');

  const amount = parseFloat(amountInput.value);
  const unitType = unitTypeSelect.value;

  let result;
  if (unitType === 'miles-to-kilometers') {
    result = amount * 1.60934; // Assuming this is the conversion logic
  } else if (unitType === 'kilometers-to-miles') {
    result = amount / 1.60934; // Assuming this is the conversion logic
  }

  resultDiv.innerHTML = `Result: ${result.toFixed(2)}`;
}