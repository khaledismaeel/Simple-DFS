#include <stdio.h>

int main() {
  int x, y;
  printf("Enter two integers: ");
  scanf("%d %d", &x, &y);
  printf("%d + %d = %d", x, y, x + y);
  return 0;
}